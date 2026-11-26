"""Crea las tablas con restricciones, carga los CSV limpios y ejecuta 12 consultas.

Uso desde la raíz de la entrega: python src/cargar_sqlite.py
No usa to_sql(replace): las claves y los CHECK del DDL permanecen activos.
"""
from pathlib import Path
import json
import re
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDEN_CARGA = [
    "dim_depot", "dim_linea", "dim_vehiculo", "dim_conductor", "dim_parada",
    "dim_tarifa", "fact_viajes", "fact_incidencias", "fact_mantenimiento",
]


def cargar_base(root=ROOT):
    root = Path(root)
    salida = root / "resultados"
    salida.mkdir(exist_ok=True)
    sql = (root / "02_sql.sql").read_text(encoding="utf-8")
    partes = re.split(r"(?m)^-- CONSULTA (\d+): (.+)$", sql)
    temporal = salida / "metrobus_temporal.db"
    if temporal.exists():
        temporal.unlink()  # Solo la base temporal de esta ejecución.
    resumen = {}
    try:
        with sqlite3.connect(temporal) as con:
            con.execute("PRAGMA foreign_keys = ON")
            con.executescript(partes[0])
            for tabla in ORDEN_CARGA:
                df = pd.read_csv(root / "data_clean" / f"{tabla}.csv")
                columnas = [r[1] for r in con.execute(f'PRAGMA table_info("{tabla}")')]
                if set(columnas) != set(df.columns):
                    faltan = set(columnas) - set(df.columns)
                    sobran = set(df.columns) - set(columnas)
                    raise ValueError(f"Esquema de {tabla}: faltan {faltan}; sobran {sobran}")
                # None se inserta como NULL; los booleanos Python se almacenan como 0/1.
                df = df[columnas].astype(object).where(df[columnas].notna(), None)
                campos = ", ".join(f'"{c}"' for c in columnas)
                placeholders = ", ".join("?" for _ in columnas)
                con.executemany(f'INSERT INTO "{tabla}" ({campos}) VALUES ({placeholders})',
                                df.itertuples(index=False, name=None))
                resumen[tabla] = con.execute(f'SELECT COUNT(*) FROM "{tabla}"').fetchone()[0]
            if con.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("Se han detectado referencias sin correspondencia")
            if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("La base SQLite no supera integrity_check")
            # Validación adicional: los campos redundantes de la incidencia deben coincidir con su viaje.
            incoherentes = con.execute("""
                SELECT COUNT(*) FROM fact_incidencias i JOIN fact_viajes v USING (viaje_id)
                WHERE i.linea_id != v.linea_id OR i.vehiculo_id != v.vehiculo_id
                   OR i.conductor_id != v.conductor_id OR i.fecha != v.fecha
            """).fetchone()[0]
            if incoherentes:
                raise ValueError(f"Incidencias incoherentes con su viaje: {incoherentes}")
            consultas = salida / "consultas_sql"
            consultas.mkdir(exist_ok=True)
            for i in range(1, len(partes), 3):
                numero, pregunta, consulta = partes[i:i+3]
                frame = pd.read_sql_query(consulta.strip(), con)
                frame.to_csv(consultas / f"consulta_{numero}.csv", index=False)
                print(f"Consulta {numero}: {len(frame)} filas. {pregunta}")
            con.commit()
        temporal.replace(salida / "metrobus.db")
    except Exception:
        if temporal.exists():
            temporal.unlink()
        raise
    (salida / "validacion_sql.json").write_text(
        json.dumps({"tablas": resumen, "foreign_key_check": "OK", "integrity_check": "OK",
                    "consultas_ejecutadas": (len(partes)-1)//3}, indent=2), encoding="utf-8")
    print("SQLite creado con restricciones activas:", salida / "metrobus.db")
    return resumen


if __name__ == "__main__":
    cargar_base()
