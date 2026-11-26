-- MetroBus Analytics | SQLite 3 | Modelo relacional y 12 preguntas de negocio.
-- Ejecutar con: python src/cargar_sqlite.py
-- El cargador crea el esquema, inserta los CSV de data_clean y exporta cada consulta.
-- Fechas ISO YYYY-MM-DD; booleanos INTEGER (0/1); NULL significa desconocido.
-- Las dimensiones describen la foto recibida: no se interpreta activo como estado histórico.
PRAGMA foreign_keys = ON;

CREATE TABLE dim_depot (
    depot_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    barrio TEXT NOT NULL,
    latitud REAL CHECK (latitud BETWEEN -90 AND 90),
    longitud REAL CHECK (longitud BETWEEN -180 AND 180),
    capacidad_vehiculos INTEGER NOT NULL CHECK (capacidad_vehiculos > 0)
);

CREATE TABLE dim_linea (
    linea_id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Urbana','Interurbana','Nocturna')),
    km_recorrido REAL NOT NULL CHECK (km_recorrido > 0),
    n_paradas INTEGER NOT NULL CHECK (n_paradas > 0),
    frecuencia_min INTEGER NOT NULL CHECK (frecuencia_min > 0)
);

CREATE TABLE dim_vehiculo (
    vehiculo_id INTEGER PRIMARY KEY,
    matricula TEXT NOT NULL UNIQUE,
    modelo TEXT NOT NULL,
    combustible TEXT CHECK (combustible IN ('Diesel','Electrico','Hibrido','Desconocido')),
    capacidad_sentados INTEGER NOT NULL CHECK (capacidad_sentados > 0),
    capacidad_total INTEGER NOT NULL CHECK (capacidad_total >= capacidad_sentados),
    anno_fabricacion INTEGER CHECK (anno_fabricacion BETWEEN 1900 AND 2025),
    anno_incorporacion INTEGER NOT NULL CHECK (anno_incorporacion BETWEEN 1900 AND 2025),
    km_totales INTEGER CHECK (km_totales >= 0),
    depot_id INTEGER NOT NULL REFERENCES dim_depot(depot_id),
    emisiones_co2_gkm REAL NOT NULL CHECK (emisiones_co2_gkm >= 0),
    en_servicio INTEGER NOT NULL CHECK (en_servicio IN (0,1)),
    combustible_inferido INTEGER NOT NULL CHECK (combustible_inferido IN (0,1)),
    anno_fabricacion_original INTEGER,
    anno_fabricacion_invalido INTEGER NOT NULL CHECK (anno_fabricacion_invalido IN (0,1)),
    km_totales_original INTEGER,
    km_totales_invalido INTEGER NOT NULL CHECK (km_totales_invalido IN (0,1))
);

CREATE TABLE dim_conductor (
    conductor_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    anno_incorporacion INTEGER NOT NULL CHECK (anno_incorporacion BETWEEN 1900 AND 2024),
    antiguedad_anos REAL CHECK (antiguedad_anos >= 0),
    turno_habitual TEXT NOT NULL,
    depot_id INTEGER NOT NULL REFERENCES dim_depot(depot_id),
    formacion TEXT NOT NULL,
    licencia_tipo TEXT NOT NULL CHECK (licencia_tipo IN ('D','D+E')),
    activo INTEGER NOT NULL CHECK (activo IN (0,1)),
    ausencias_2024 INTEGER NOT NULL CHECK (ausencias_2024 >= 0),
    antiguedad_inferida INTEGER NOT NULL CHECK (antiguedad_inferida IN (0,1))
);

CREATE TABLE dim_parada (
    parada_id INTEGER PRIMARY KEY,
    nombre_parada TEXT NOT NULL,
    barrio TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Intermedia','Intercambiador','Cabecera')),
    latitud REAL CHECK (latitud BETWEEN -90 AND 90),
    longitud REAL CHECK (longitud BETWEEN -180 AND 180),
    accesible_silla INTEGER CHECK (accesible_silla IN (0,1)),
    marquesina INTEGER NOT NULL CHECK (marquesina IN (0,1)),
    panel_informacion INTEGER NOT NULL CHECK (panel_informacion IN (0,1)),
    activa INTEGER NOT NULL CHECK (activa IN (0,1)),
    latitud_original REAL,
    latitud_invalida INTEGER NOT NULL CHECK (latitud_invalida IN (0,1))
);

CREATE TABLE dim_tarifa (
    tarifa_id INTEGER PRIMARY KEY,
    tipo_titulo TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    precio_eur REAL NOT NULL CHECK (precio_eur >= 0),
    es_abono INTEGER NOT NULL CHECK (es_abono IN (0,1)),
    bonificado INTEGER NOT NULL CHECK (bonificado IN (0,1))
);

CREATE TABLE fact_viajes (
    viaje_id INTEGER PRIMARY KEY,
    linea_id INTEGER NOT NULL REFERENCES dim_linea(linea_id),
    vehiculo_id INTEGER NOT NULL REFERENCES dim_vehiculo(vehiculo_id),
    conductor_id INTEGER NOT NULL REFERENCES dim_conductor(conductor_id),
    parada_origen_id INTEGER NOT NULL REFERENCES dim_parada(parada_id),
    parada_destino_id INTEGER NOT NULL REFERENCES dim_parada(parada_id),
    fecha TEXT NOT NULL CHECK (date(fecha) IS NOT NULL),
    anno INTEGER NOT NULL CHECK (anno = CAST(strftime('%Y', fecha) AS INTEGER)),
    mes INTEGER NOT NULL CHECK (mes = CAST(strftime('%m', fecha) AS INTEGER)),
    dia_semana TEXT NOT NULL,
    es_festivo INTEGER NOT NULL CHECK (es_festivo IN (0,1)),
    franja_horaria TEXT NOT NULL,
    hora_salida_prog TEXT NOT NULL,
    hora_salida_real TEXT NOT NULL,
    hora_llegada_real TEXT NOT NULL,
    retraso_salida_min INTEGER,
    duracion_real_min INTEGER NOT NULL CHECK (duracion_real_min >= 0),
    pasajeros_subidos INTEGER CHECK (pasajeros_subidos >= 0),
    ocupacion_pct REAL CHECK (ocupacion_pct BETWEEN 0 AND 1),
    km_programados REAL NOT NULL CHECK (km_programados >= 0),
    km_recorridos REAL NOT NULL CHECK (km_recorridos >= 0),
    viaje_completado INTEGER NOT NULL CHECK (viaje_completado IN (0,1)),
    consumo REAL CHECK (consumo >= 0),
    tarifa_predominante_id INTEGER NOT NULL REFERENCES dim_tarifa(tarifa_id),
    pasajeros_estimados REAL CHECK (pasajeros_estimados >= 0),
    pasajeros_imputados INTEGER NOT NULL CHECK (pasajeros_imputados IN (0,1)),
    consumo_ausente INTEGER NOT NULL CHECK (consumo_ausente IN (0,1)),
    retraso_salida_min_original INTEGER,
    retraso_corregido INTEGER NOT NULL CHECK (retraso_corregido IN (0,1)),
    es_retrasado INTEGER CHECK (es_retrasado IN (0,1)),
    en_periodo INTEGER NOT NULL CHECK (en_periodo IN (0,1)),
    franja_id INTEGER NOT NULL,
    fecha_franja_id TEXT NOT NULL,
    vehiculo_previo_incorporacion INTEGER NOT NULL CHECK (vehiculo_previo_incorporacion IN (0,1))
);

CREATE TABLE fact_incidencias (
    incidencia_id INTEGER PRIMARY KEY,
    viaje_id INTEGER NOT NULL REFERENCES fact_viajes(viaje_id),
    vehiculo_id INTEGER NOT NULL REFERENCES dim_vehiculo(vehiculo_id),
    conductor_id INTEGER NOT NULL REFERENCES dim_conductor(conductor_id),
    linea_id INTEGER NOT NULL REFERENCES dim_linea(linea_id),
    fecha TEXT NOT NULL CHECK (date(fecha) IS NOT NULL),
    anno INTEGER NOT NULL CHECK (anno = CAST(strftime('%Y', fecha) AS INTEGER)),
    mes INTEGER NOT NULL CHECK (mes = CAST(strftime('%m', fecha) AS INTEGER)),
    hora_incidencia TEXT NOT NULL,
    tipo_incidencia TEXT NOT NULL,
    categoria TEXT NOT NULL,
    severidad TEXT NOT NULL CHECK (severidad IN ('Baja','Media','Alta','Critica')),
    requiere_retirada INTEGER NOT NULL CHECK (requiere_retirada IN (0,1)),
    duracion_resolucion_min INTEGER NOT NULL CHECK (duracion_resolucion_min >= 0),
    vehiculo_sustituto INTEGER NOT NULL CHECK (vehiculo_sustituto IN (0,1)),
    coste_estimado_eur REAL CHECK (coste_estimado_eur >= 0),
    en_periodo INTEGER NOT NULL CHECK (en_periodo IN (0,1)),
    franja_horaria TEXT NOT NULL,
    franja_id INTEGER NOT NULL,
    fecha_franja_id TEXT NOT NULL
);

CREATE TABLE fact_mantenimiento (
    mantenimiento_id INTEGER PRIMARY KEY,
    vehiculo_id INTEGER NOT NULL REFERENCES dim_vehiculo(vehiculo_id),
    depot_id INTEGER NOT NULL REFERENCES dim_depot(depot_id),
    fecha_entrada TEXT NOT NULL CHECK (date(fecha_entrada) IS NOT NULL),
    fecha_salida TEXT NOT NULL CHECK (date(fecha_salida) IS NOT NULL AND fecha_salida >= fecha_entrada),
    anno INTEGER NOT NULL CHECK (anno = CAST(strftime('%Y', fecha_entrada) AS INTEGER)),
    mes INTEGER NOT NULL CHECK (mes = CAST(strftime('%m', fecha_entrada) AS INTEGER)),
    tipo_mantenimiento TEXT NOT NULL,
    categoria TEXT CHECK (categoria IN ('Preventivo','Correctivo','Legal','Estetico')),
    es_correctivo INTEGER NOT NULL CHECK (es_correctivo IN (0,1)),
    dias_fuera_servicio INTEGER NOT NULL CHECK (dias_fuera_servicio >= 0),
    km_en_revision INTEGER NOT NULL CHECK (km_en_revision >= 0),
    coste_eur REAL CHECK (coste_eur >= 0),
    proveedor TEXT NOT NULL,
    garantia_meses INTEGER NOT NULL CHECK (garantia_meses >= 0),
    coste_eur_original REAL,
    coste_invalido INTEGER NOT NULL CHECK (coste_invalido IN (0,1)),
    categoria_inferida INTEGER NOT NULL CHECK (categoria_inferida IN (0,1)),
    en_periodo INTEGER NOT NULL CHECK (en_periodo IN (0,1)),
    franja_id INTEGER NOT NULL,
    fecha_franja_id TEXT NOT NULL
);

CREATE INDEX idx_viajes_fecha_linea ON fact_viajes(fecha, linea_id);
CREATE INDEX idx_viajes_vehiculo ON fact_viajes(vehiculo_id);
CREATE INDEX idx_incidencias_viaje ON fact_incidencias(viaje_id);
CREATE INDEX idx_incidencias_fecha_linea ON fact_incidencias(fecha, linea_id);
CREATE INDEX idx_mantenimiento_fecha_vehiculo ON fact_mantenimiento(fecha_entrada, vehiculo_id);

-- Vistas con el mismo periodo que el dashboard: inicio y cierre incluidos.
CREATE VIEW v_viajes_periodo AS
SELECT * FROM fact_viajes WHERE fecha BETWEEN '2022-01-01' AND '2024-12-31';
CREATE VIEW v_incidencias_periodo AS
SELECT * FROM fact_incidencias WHERE fecha BETWEEN '2022-01-01' AND '2024-12-31';
CREATE VIEW v_mantenimiento_periodo AS
SELECT * FROM fact_mantenimiento WHERE fecha_entrada BETWEEN '2022-01-01' AND '2024-12-31';

-- CONSULTA 01: ¿Cuál es el volumen operativo y qué cobertura tienen pasajeros y puntualidad?
SELECT COUNT(*) AS viajes,
       SUM(pasajeros_subidos) AS pasajeros_observados,
       COUNT(pasajeros_subidos) AS viajes_con_pasajeros,
       ROUND(100.0 * COUNT(pasajeros_subidos) / NULLIF(COUNT(*),0), 3) AS cobertura_pasajeros_pct,
       ROUND(100.0 * AVG(CASE WHEN retraso_salida_min IS NULL THEN NULL
                             WHEN retraso_salida_min <= 5 THEN 1.0 ELSE 0.0 END),3) AS puntualidad_pct,
       ROUND(AVG(retraso_salida_min),3) AS retraso_medio_min,
       ROUND(100.0 * AVG(ocupacion_pct),3) AS ocupacion_media_pct,
       ROUND(100.0 * AVG(viaje_completado),3) AS viajes_completados_pct,
       ROUND(SUM(km_recorridos),2) AS km_recorridos
FROM v_viajes_periodo;

-- CONSULTA 02: ¿Qué líneas concentran más demanda observada y pasajeros por expedición informada?
SELECT l.codigo, l.nombre, COUNT(*) AS viajes, SUM(v.pasajeros_subidos) AS pasajeros_observados,
       ROUND(AVG(v.pasajeros_subidos),2) AS pasajeros_por_viaje_informado,
       COUNT(v.pasajeros_subidos) AS viajes_con_pasajeros,
       ROUND(100.0 * AVG(v.ocupacion_pct),2) AS ocupacion_media_pct
FROM v_viajes_periodo v JOIN dim_linea l USING (linea_id)
GROUP BY l.linea_id, l.codigo, l.nombre ORDER BY pasajeros_observados DESC;

-- CONSULTA 03: ¿Qué líneas tienen mayor proporción de salidas con más de cinco minutos de retraso?
SELECT l.codigo, COUNT(v.retraso_salida_min) AS viajes_con_retraso_informado,
       ROUND(100.0 * AVG(CASE WHEN v.retraso_salida_min IS NULL THEN NULL
                             WHEN v.retraso_salida_min > 5 THEN 1.0 ELSE 0.0 END),2) AS retrasados_pct,
       ROUND(AVG(v.retraso_salida_min),2) AS retraso_medio_min,
       MAX(v.retraso_salida_min) AS retraso_maximo_min
FROM v_viajes_periodo v JOIN dim_linea l USING (linea_id)
GROUP BY l.linea_id, l.codigo ORDER BY retrasados_pct DESC;

-- CONSULTA 04: ¿Qué combinaciones de línea y franja requieren estudiar un refuerzo de capacidad?
SELECT l.codigo, v.franja_horaria, COUNT(*) AS viajes,
       SUM(v.pasajeros_subidos) AS pasajeros_observados,
       ROUND(AVG(v.pasajeros_subidos),2) AS pasajeros_por_viaje_informado,
       ROUND(100.0 * AVG(v.ocupacion_pct),2) AS ocupacion_media_pct
FROM v_viajes_periodo v JOIN dim_linea l USING (linea_id)
GROUP BY l.linea_id, l.codigo, v.franja_horaria
ORDER BY pasajeros_observados DESC LIMIT 15;

-- CONSULTA 05: ¿Cómo evoluciona la tasa de incidencias por 1.000 viajes entre años?
WITH viajes AS (
    SELECT anno, COUNT(*) AS viajes FROM v_viajes_periodo GROUP BY anno
), incidencias AS (
    SELECT anno, COUNT(*) AS incidencias FROM v_incidencias_periodo GROUP BY anno
)
SELECT v.anno, v.viajes, COALESCE(i.incidencias,0) AS incidencias,
       ROUND(1000.0 * COALESCE(i.incidencias,0) / NULLIF(v.viajes,0),2) AS incidencias_por_1000_viajes
FROM viajes v LEFT JOIN incidencias i USING (anno) ORDER BY v.anno;

-- CONSULTA 06: ¿Qué líneas presentan mayor tasa de incidencias, normalizando por viajes?
WITH viajes AS (
    SELECT linea_id, COUNT(*) AS viajes FROM v_viajes_periodo GROUP BY linea_id
), incidencias AS (
    SELECT linea_id, COUNT(*) AS incidencias, SUM(coste_estimado_eur) AS coste_estimado_eur
    FROM v_incidencias_periodo GROUP BY linea_id
)
SELECT l.codigo, v.viajes, COALESCE(i.incidencias,0) AS incidencias,
       ROUND(1000.0 * COALESCE(i.incidencias,0)/NULLIF(v.viajes,0),2) AS incidencias_por_1000_viajes,
       ROUND(i.coste_estimado_eur,2) AS coste_estimado_eur
FROM viajes v JOIN dim_linea l USING (linea_id)
LEFT JOIN incidencias i USING (linea_id) ORDER BY incidencias_por_1000_viajes DESC;

-- CONSULTA 07: ¿Qué tipos de incidencia combinan frecuencia, gravedad y coste estimado?
SELECT tipo_incidencia, categoria, severidad, COUNT(*) AS incidencias,
       ROUND(SUM(coste_estimado_eur),2) AS coste_estimado_eur,
       ROUND(AVG(duracion_resolucion_min),2) AS resolucion_media_min,
       SUM(requiere_retirada) AS retiradas
FROM v_incidencias_periodo GROUP BY tipo_incidencia, categoria, severidad
ORDER BY coste_estimado_eur DESC;

-- CONSULTA 08: ¿Cuánto mantenimiento válido se registra cada año y qué parte no tiene coste utilizable?
SELECT anno, COUNT(*) AS intervenciones, COUNT(coste_eur) AS intervenciones_con_coste,
       COUNT(*) - COUNT(coste_eur) AS costes_no_utilizables,
       ROUND(SUM(coste_eur),2) AS coste_observado_valido_eur,
       ROUND(AVG(coste_eur),2) AS coste_medio_intervencion_informada_eur,
       ROUND(100.0 * AVG(es_correctivo),2) AS correctivo_pct
FROM v_mantenimiento_periodo GROUP BY anno ORDER BY anno;

-- CONSULTA 09: ¿Cómo varía el coste de mantenimiento por 1.000 km entre combustibles?
-- Se agregan por separado hechos con distinta granularidad; nunca se unen sus filas directamente.
WITH viajes AS (
    SELECT vehiculo_id, SUM(km_recorridos) AS km FROM v_viajes_periodo GROUP BY vehiculo_id
), mantenimiento AS (
    SELECT vehiculo_id, SUM(coste_eur) AS coste, COUNT(*) AS intervenciones,
           COUNT(coste_eur) AS con_coste FROM v_mantenimiento_periodo GROUP BY vehiculo_id
)
SELECT d.combustible, COUNT(*) AS vehiculos_con_viajes,
       ROUND(SUM(v.km),2) AS km_recorridos,
       ROUND(SUM(COALESCE(m.coste,0)),2) AS coste_observado_valido_eur,
       ROUND(1000.0 * SUM(COALESCE(m.coste,0))/NULLIF(SUM(v.km),0),2) AS coste_por_1000_km_eur,
       SUM(COALESCE(m.intervenciones,0)) AS intervenciones,
       SUM(COALESCE(m.con_coste,0)) AS intervenciones_con_coste
FROM viajes v JOIN dim_vehiculo d USING (vehiculo_id)
LEFT JOIN mantenimiento m USING (vehiculo_id)
GROUP BY d.combustible ORDER BY coste_por_1000_km_eur DESC;

-- CONSULTA 10: ¿Qué vehículos justifican una revisión por coste y tasa de incidencias?
WITH v AS (
    SELECT vehiculo_id, COUNT(*) AS viajes, SUM(km_recorridos) AS km
    FROM v_viajes_periodo GROUP BY vehiculo_id
), i AS (
    SELECT vehiculo_id, COUNT(*) AS incidencias FROM v_incidencias_periodo GROUP BY vehiculo_id
), m AS (
    SELECT vehiculo_id, SUM(coste_eur) AS coste, COUNT(coste_eur) AS con_coste,
           COUNT(*) AS intervenciones FROM v_mantenimiento_periodo GROUP BY vehiculo_id
)
SELECT d.vehiculo_id, d.matricula, d.combustible, v.viajes, ROUND(v.km,2) AS km,
       COALESCE(i.incidencias,0) AS incidencias,
       ROUND(1000.0 * COALESCE(i.incidencias,0)/NULLIF(v.viajes,0),2) AS incidencias_por_1000_viajes,
       ROUND(m.coste,2) AS coste_observado_valido_eur,
       ROUND(1000.0 * m.coste/NULLIF(v.km,0),2) AS coste_por_1000_km_eur,
       m.con_coste, m.intervenciones
FROM v JOIN dim_vehiculo d USING (vehiculo_id)
LEFT JOIN i USING (vehiculo_id) LEFT JOIN m USING (vehiculo_id)
ORDER BY coste_por_1000_km_eur DESC LIMIT 15;

-- CONSULTA 11: ¿Qué títulos predominan en las expediciones y qué proporción de viajes representan?
-- La tarifa predominante no identifica todos los billetes vendidos: no equivale a ingresos.
SELECT t.tipo_titulo, t.categoria, COUNT(*) AS viajes,
       ROUND(100.0 * COUNT(*)/(SELECT COUNT(*) FROM v_viajes_periodo),2) AS viajes_pct
FROM v_viajes_periodo v JOIN dim_tarifa t ON v.tarifa_predominante_id=t.tarifa_id
GROUP BY t.tarifa_id, t.tipo_titulo, t.categoria ORDER BY viajes DESC;

-- CONSULTA 12: ¿Qué líneas cambian su posición en demanda entre años?
WITH demanda AS (
    SELECT v.anno, l.codigo, SUM(v.pasajeros_subidos) AS pasajeros_observados
    FROM v_viajes_periodo v JOIN dim_linea l USING (linea_id)
    GROUP BY v.anno, l.codigo
)
SELECT anno, codigo, pasajeros_observados,
       DENSE_RANK() OVER (PARTITION BY anno ORDER BY pasajeros_observados DESC) AS posicion_anual
FROM demanda ORDER BY anno, posicion_anual;
