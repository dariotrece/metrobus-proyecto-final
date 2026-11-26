"""Limpieza trazable de MetroBus; los CSV de data/ nunca se sobrescriben.

Ejecutar: python src/preparar_datos.py
Las reglas distinguen correcciones demostrables, estimaciones y datos desconocidos.
"""

from pathlib import Path
import hashlib

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INICIO = "2022-01-01"
CIERRE = "2024-12-31"
CLAVES = {
    "dim_depot": "depot_id", "dim_linea": "linea_id",
    "dim_vehiculo": "vehiculo_id", "dim_conductor": "conductor_id",
    "dim_parada": "parada_id", "dim_tarifa": "tarifa_id",
    "fact_viajes": "viaje_id", "fact_incidencias": "incidencia_id",
    "fact_mantenimiento": "mantenimiento_id",
}
RELACIONES = [
    ("dim_vehiculo", "depot_id", "dim_depot", "depot_id"),
    ("dim_conductor", "depot_id", "dim_depot", "depot_id"),
    ("fact_viajes", "linea_id", "dim_linea", "linea_id"),
    ("fact_viajes", "vehiculo_id", "dim_vehiculo", "vehiculo_id"),
    ("fact_viajes", "conductor_id", "dim_conductor", "conductor_id"),
    ("fact_viajes", "parada_origen_id", "dim_parada", "parada_id"),
    ("fact_viajes", "parada_destino_id", "dim_parada", "parada_id"),
    ("fact_viajes", "tarifa_predominante_id", "dim_tarifa", "tarifa_id"),
    ("fact_incidencias", "viaje_id", "fact_viajes", "viaje_id"),
    ("fact_incidencias", "linea_id", "dim_linea", "linea_id"),
    ("fact_incidencias", "vehiculo_id", "dim_vehiculo", "vehiculo_id"),
    ("fact_incidencias", "conductor_id", "dim_conductor", "conductor_id"),
    ("fact_mantenimiento", "vehiculo_id", "dim_vehiculo", "vehiculo_id"),
    ("fact_mantenimiento", "depot_id", "dim_depot", "depot_id"),
]


def cargar_originales(root=ROOT):
    return {nombre: pd.read_csv(root / "data" / f"{nombre}.csv")
            for nombre in CLAVES}


def minutos_hora(serie):
    """HH:MM a minutos desde medianoche; falla ante formatos desconocidos."""
    partes = serie.str.split(":", expand=True).astype(int)
    assert partes[0].between(0, 23).all() and partes[1].between(0, 59).all()
    return partes[0] * 60 + partes[1]


def validar_relaciones(tablas):
    resultados = []
    for nombre, clave in CLAVES.items():
        s = tablas[nombre][clave]
        fallos = int(s.isna().sum() + s.duplicated().sum())
        resultados.append({"regla": f"PK {nombre}.{clave}", "incumplimientos": fallos})
    for hija, fk, padre, pk in RELACIONES:
        s = tablas[hija][fk]
        fallos = int((s.isna() | ~s.isin(tablas[padre][pk])).sum())
        resultados.append({"regla": f"FK {hija}.{fk} -> {padre}.{pk}",
                           "incumplimientos": fallos})
    return pd.DataFrame(resultados)


def limpiar(tablas_raw):
    tablas = {nombre: df.copy() for nombre, df in tablas_raw.items()}
    log = []

    def registrar(tabla, campo, problema, filas, decision, justificacion):
        log.append({"tabla": tabla, "campo": campo, "tipo_problema": problema,
                    "frecuencia": int(filas), "decision": decision,
                    "justificacion": justificacion})

    viajes = tablas["fact_viajes"]
    incidencias = tablas["fact_incidencias"]
    mantenimiento = tablas["fact_mantenimiento"]
    vehiculos = tablas["dim_vehiculo"]
    conductores = tablas["dim_conductor"]
    paradas = tablas["dim_parada"]

    # Conversión estricta: no esconder silenciosamente una fecha no interpretable.
    for nombre, campos in {
        "fact_viajes": ["fecha"], "fact_incidencias": ["fecha"],
        "fact_mantenimiento": ["fecha_entrada", "fecha_salida"],
    }.items():
        for campo in campos:
            tablas[nombre][campo] = pd.to_datetime(tablas[nombre][campo], format="%Y-%m-%d")

    for df, tabla, campo, cambios in [
        (vehiculos, "dim_vehiculo", "combustible", {"diesel": "Diesel"}),
        (conductores, "dim_conductor", "turno_habitual", {"manana": "Manana (06-14h)"}),
        (paradas, "dim_parada", "barrio", {"centro": "Centro", "BARRIO NORTE": "Barrio Norte"}),
    ]:
        n = df[campo].isin(cambios).sum()
        df[campo] = df[campo].replace(cambios)
        registrar(tabla, campo, "Categoría inconsistente", n, str(cambios),
                  "Unificar etiquetas equivalentes; no cambia su significado.")

    dias = viajes.fecha.dt.dayofweek.map(dict(enumerate(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])))
    registrar("fact_viajes", "dia_semana", "Etiqueta inconsistente", viajes.dia_semana.ne(dias).sum(),
              "Recalcular desde fecha con un mapa explícito.",
              "Fecha validada es la fuente; evita etiquetas duplicadas y depende menos del idioma del sistema.")
    viajes["dia_semana"] = dias

    # Solo inferir cuando cada grupo observado tiene una única categoría, no una moda ambigua.
    for df, tabla, campo, grupo, bandera in [
        (vehiculos, "dim_vehiculo", "combustible", "modelo", "combustible_inferido"),
        (mantenimiento, "fact_mantenimiento", "categoria", "tipo_mantenimiento", "categoria_inferida"),
    ]:
        referencia = df.dropna(subset=[campo]).groupby(grupo)[campo]
        unicos = referencia.nunique().eq(1)
        mapa = referencia.first().loc[unicos]
        antes = df[campo].isna()
        df[campo] = df[campo].fillna(df[grupo].map(mapa))
        df[bandera] = antes & df[campo].notna()
        registrar(tabla, campo, "Nulo", antes.sum(),
                  f"Inferir solo con categoría única por {grupo}; marcar {bandera}.",
                  "Correspondencia unívoca observada; una categoría ambigua quedaría nula.")

    conductores["antiguedad_inferida"] = conductores["antiguedad_anos"].isna()
    conductores["antiguedad_anos"] = conductores["antiguedad_anos"].fillna(
        2024 - conductores["anno_incorporacion"])
    registrar("dim_conductor", "antiguedad_anos", "Nulo", conductores.antiguedad_inferida.sum(),
              "Calcular 2024 - anno_incorporacion, con bandera.",
              "Antigüedad en años enteros al cierre; coincide con los valores informados.")

    for campo, mascara in {
        "anno_fabricacion": vehiculos.anno_fabricacion.gt(vehiculos.anno_incorporacion),
        "km_totales": vehiculos.km_totales.lt(0),
    }.items():
        vehiculos[f"{campo}_original"] = vehiculos[campo]
        vehiculos[f"{campo}_invalido"] = mascara
        vehiculos[campo] = vehiculos[campo].mask(mascara).astype("Int64")
        registrar("dim_vehiculo", campo, "Fuera de dominio", mascara.sum(),
                  "Conservar original y bandera; valor analítico nulo.",
                  "No existe evidencia para reconstruir el valor real.")

    paradas["latitud_original"] = paradas.latitud
    paradas["latitud_invalida"] = paradas.latitud.notna() & ~paradas.latitud.between(-90, 90)
    paradas["latitud"] = paradas.latitud.mask(paradas.latitud_invalida)
    registrar("dim_parada", "latitud", "Fuera de dominio", paradas.latitud_invalida.sum(),
              "999 pasa a nulo, con original y bandera.", "Una latitud debe estar entre -90 y 90 grados.")
    registrar("dim_parada", "latitud", "Nulo original", tablas_raw["dim_parada"].latitud.isna().sum(),
              "Mantener desconocido; excluir de mapas puntuales.", "Una mediana de barrio inventaría una ubicación.")
    registrar("dim_parada", "accesible_silla", "Nulo", paradas.accesible_silla.isna().sum(),
              "Mantener desconocido; informar cobertura.", "La accesibilidad requiere comprobación física, no imputación por mayoría.")
    paradas["accesible_silla"] = paradas.accesible_silla.astype("boolean")

    viajes["pasajeros_imputados"] = viajes.pasajeros_subidos.isna()
    mediana = viajes.groupby(["linea_id", "franja_horaria"])["pasajeros_subidos"].transform("median")
    viajes["pasajeros_estimados"] = viajes.pasajeros_subidos.fillna(mediana).round().astype("Int64")
    viajes["pasajeros_subidos"] = viajes.pasajeros_subidos.astype("Int64")
    registrar("fact_viajes", "pasajeros_subidos", "Nulo", viajes.pasajeros_imputados.sum(),
              "Conservar observado nulo; estimación separada con mediana línea/franja y bandera.",
              "El KPI principal suma pasajeros observados; estimados solo para sensibilidad.")
    viajes["consumo_ausente"] = viajes.consumo.isna()
    registrar("fact_viajes", "consumo", "Nulo", viajes.consumo_ausente.sum(),
              "Mantener nulo y medir cobertura.",
              "No hay unidad documentada ni evidencia para imputar. No comparar tecnologías con una suma de consumo.")

    viajes["retraso_salida_min_original"] = viajes.retraso_salida_min
    viajes["retraso_corregido"] = viajes.retraso_salida_min.eq(-99)
    # Convertir las dos horas a minutos y restarlas.
    minutos_reales = minutos_hora(viajes["hora_salida_real"])
    minutos_programados = minutos_hora(viajes["hora_salida_prog"])
    diferencia = minutos_reales - minutos_programados

    # Una diferencia de -1430 minutos representa 10 minutos al cruzar medianoche.
    # Se supone que el desvío real está entre -12 y 12 horas.
    retraso_horas = diferencia.copy()
    retraso_horas.loc[diferencia < -720] += 1440
    retraso_horas.loc[diferencia >= 720] -= 1440
    assert viajes.loc[~viajes.retraso_corregido, "retraso_salida_min"].eq(
        retraso_horas.loc[~viajes.retraso_corregido]).all()
    viajes.loc[viajes.retraso_corregido, "retraso_salida_min"] = retraso_horas[viajes.retraso_corregido]
    viajes["es_retrasado"] = viajes.retraso_salida_min.gt(5)
    registrar("fact_viajes", "retraso_salida_min", "Código -99 incompatible con horas", viajes.retraso_corregido.sum(),
              "Recuperar diferencia real-programada en [-720,720); original y bandera.",
              "Las otras 49.920 filas concuerdan con la fórmula. Supuesto: desviación menor de 12 horas.")

    mantenimiento["coste_eur_original"] = mantenimiento.coste_eur
    mantenimiento["coste_invalido"] = mantenimiento.coste_eur.lt(0)
    mantenimiento["coste_eur"] = mantenimiento.coste_eur.mask(mantenimiento.coste_invalido)
    registrar("fact_mantenimiento", "coste_eur", "Importe negativo sin tipo de abono", mantenimiento.coste_invalido.sum(),
              "Mantener registro; importe analítico nulo, original y bandera. Coste observado válido.",
              "No hay evidencia de abono ni del importe correcto. El KPI informa cobertura, sin presentar estimaciones como coste real.")

    for df, campo in [(viajes, "fecha"), (incidencias, "fecha"), (mantenimiento, "fecha_entrada")]:
        df["en_periodo"] = df[campo].between(INICIO, CIERRE)
    registrar("fact_mantenimiento", "fecha_entrada", "Fuera de periodo", (~mantenimiento.en_periodo).sum(),
              "Conservar filas; excluir del reporting 2022-2024 por fecha de entrada.",
              "Cierre común y reproducible; no se trasladan costes a 2024.")
    incorporacion = vehiculos.set_index("vehiculo_id").anno_incorporacion
    viajes["vehiculo_previo_incorporacion"] = viajes.fecha.dt.year.lt(viajes.vehiculo_id.map(incorporacion))
    registrar("fact_viajes", "fecha / anno_incorporacion vehículo", "Cronología de dimensión incompatible", viajes.vehiculo_previo_incorporacion.sum(),
              "Marcar y conservar viajes; no usar año incorporación para disponibilidad histórica.",
              "La dimensión es una instantánea sintética, no un historial fiable de altas; requiere aclaración de origen.")

    # Dimensiones temporales. Sin franja distingue mantenimiento, que no tiene hora.
    franjas = ["Sin franja", "Madrugada", "Manana punta", "Valle manana", "Tarde", "Tarde punta", "Noche"]
    dim_franja = pd.DataFrame({"franja_id": range(len(franjas)), "franja_horaria": franjas,
                              "orden": range(len(franjas))})
    mapa_franja = dim_franja.set_index("franja_horaria").franja_id
    incidencias["franja_horaria"] = incidencias.viaje_id.map(viajes.set_index("viaje_id").franja_horaria)
    for df, fecha in [(viajes, "fecha"), (incidencias, "fecha"), (mantenimiento, "fecha_entrada")]:
        df["franja_id"] = df.franja_horaria.map(mapa_franja) if "franja_horaria" in df else 0
        df["fecha_franja_id"] = df[fecha].dt.strftime("%Y-%m-%d") + "|" + df.franja_id.astype(str)
    calendario = pd.DataFrame({"fecha": pd.date_range(INICIO, "2025-12-31")})
    calendario["anno"] = calendario.fecha.dt.year
    calendario["mes"] = calendario.fecha.dt.month
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    calendario["mes_nombre"] = calendario.mes.map(dict(enumerate(meses, 1)))
    calendario["trimestre"] = calendario.fecha.dt.quarter
    calendario["semana_iso"] = calendario.fecha.dt.isocalendar().week.astype(int)
    calendario["anno_iso"] = calendario.fecha.dt.isocalendar().year.astype(int)
    calendario["dia_semana"] = calendario.fecha.dt.dayofweek + 1
    calendario["es_fin_semana"] = calendario.dia_semana.ge(6)
    calendario_franja = calendario.merge(dim_franja, how="cross")
    calendario_franja["fecha_franja_id"] = calendario_franja.fecha.dt.strftime("%Y-%m-%d") + "|" + calendario_franja.franja_id.astype(str)
    tablas.update(dim_calendario=calendario, dim_franja=dim_franja,
                  dim_calendario_franja=calendario_franja)
    return tablas, pd.DataFrame(log)


def main(root=ROOT):
    raw = cargar_originales(root)
    controles = validar_relaciones(raw)
    assert controles.incumplimientos.sum() == 0, controles.to_string(index=False)
    tablas, log = limpiar(raw)
    for nombre in CLAVES:
        assert len(tablas[nombre]) == len(raw[nombre]), f"Cambio de granularidad: {nombre}"
    assert tablas["fact_viajes"].pasajeros_estimados.notna().all()
    assert tablas["fact_mantenimiento"].coste_eur.dropna().ge(0).all()
    assert tablas["dim_calendario"].fecha.is_unique
    assert tablas["dim_calendario_franja"].fecha_franja_id.is_unique
    for nombre in ["fact_viajes", "fact_incidencias", "fact_mantenimiento"]:
        assert tablas[nombre].fecha_franja_id.isin(tablas["dim_calendario_franja"].fecha_franja_id).all()
    destino, resultados = root / "data_clean", root / "resultados"
    destino.mkdir(exist_ok=True)
    resultados.mkdir(exist_ok=True)
    for nombre, df in tablas.items():
        df.to_csv(destino / f"{nombre}.csv", index=False, date_format="%Y-%m-%d")
    log.to_csv(resultados / "calidad_decisiones.csv", index=False)
    controles.to_csv(resultados / "calidad_integridad.csv", index=False)
    manifest = [{"archivo": f"data/{n}.csv", "filas": len(df),
                 "sha256": hashlib.sha256((root / "data" / f"{n}.csv").read_bytes()).hexdigest()}
                for n, df in raw.items()]
    pd.DataFrame(manifest).to_csv(resultados / "calidad_fuentes.csv", index=False)
    print(f"ETL completado: {len(raw)} tablas originales, {len(log)} decisiones, sin pérdida de filas.")
    print(f"Datos preparados en {destino}")
    return tablas


if __name__ == "__main__":
    main()
