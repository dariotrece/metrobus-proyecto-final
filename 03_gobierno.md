# Gobierno del dato de MetroBus

Responsable del análisis: Darío Pérez Lorenzo. Periodo de reporting: 2022-01-01 a 2024-12-31.

## 1. Alcance, procedencia y responsabilidades

Los nueve CSV son datos sintéticos facilitados por el curso. `data/` conserva los originales. `data_clean/` es la capa preparada y `resultados/metrobus.db` la carga relacional. `resultados/calidad_fuentes.csv` registra filas y SHA-256 para detectar cambios de origen. La ejecución reconstruye resultados desde los originales, sin dependencias de rutas del autor.

Operaciones valida puntualidad, demanda y granularidad de expediciones. Taller valida costes y categorías. Flota valida tecnología e historial de vehículos. Planificación valida servicio y franjas. El analista documenta reglas y excepciones; no sustituye al propietario de negocio.

## 2. Diccionario del modelo

Los tipos son los declarados en SQLite. Booleanos se guardan como 0/1; NULL significa desconocido. Incluyo campos originales y columnas derivadas de auditoría.


### dim_depot

Granularidad: una cochera. 3 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| depot_id | INTEGER | Identificador de cochera | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| nombre | TEXT | Nombre de la entidad | Texto informado; sin catálogo externo disponible; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| barrio | TEXT | Barrio de localización | Barrio Norte; Barrio Sur; Centro; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| latitud | REAL | Coordenada geográfica norte-sur, en grados | Regla SQL: latitud BETWEEN -90 AND 90; permite NULL | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| longitud | REAL | Coordenada geográfica este-oeste, en grados | Regla SQL: longitud BETWEEN -180 AND 180; permite NULL | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| capacidad_vehiculos | INTEGER | Plazas para vehículos en la cochera | Regla SQL: capacidad_vehiculos > 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |


### dim_linea

Granularidad: una línea. 10 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| linea_id | INTEGER | Identificador de línea | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| codigo | TEXT | Código comercial de la línea | L1; L2; L3; L4; L5; L6; L7; L8; L9; N1; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| nombre | TEXT | Nombre de la entidad | Texto informado; sin catálogo externo disponible; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| tipo | TEXT | Clasificación de la entidad | Regla SQL: tipo IN ('Urbana','Interurbana','Nocturna'); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| km_recorrido | REAL | Longitud del recorrido de la línea, en km | Regla SQL: km_recorrido > 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| n_paradas | INTEGER | Número de paradas de la línea | Regla SQL: n_paradas > 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| frecuencia_min | INTEGER | Intervalo programado entre servicios, en minutos | Regla SQL: frecuencia_min > 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |


### dim_vehiculo

Granularidad: un vehículo. 45 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| vehiculo_id | INTEGER | Identificador de vehículo | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| matricula | TEXT | Matrícula identificativa del vehículo | Texto informado; sin catálogo externo disponible; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| modelo | TEXT | Modelo comercial del vehículo | BYD eBus-12; Irizar ie bus; Iveco Urbanway; MAN Lions City; MAN Lions City G; Mercedes-Benz Citaro; Mercedes-Benz eCitaro; Scania Citywide; Solaris Urbino 12; Solaris Urbino 18; Volvo 7900 Hybrid; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| combustible | TEXT | Tecnología energética registrada | Regla SQL: combustible IN ('Diesel','Electrico','Hibrido','Desconocido'); permite NULL | 1 nulos originales (2.222%) Categoría inconsistente: 1; {'diesel': 'Diesel'} Nulo: 1; Inferir solo con categoría única por modelo; marcar combustible_inferido. |
| capacidad_sentados | INTEGER | Plazas sentadas | Regla SQL: capacidad_sentados > 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| capacidad_total | INTEGER | Capacidad total de personas | Regla SQL: capacidad_total >= capacidad_sentados; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| anno_fabricacion | INTEGER | Año de fabricación | Regla SQL: anno_fabricacion BETWEEN 1900 AND 2025; permite NULL | Fuera de dominio: 1; Conservar original y bandera; valor analítico nulo. |
| anno_incorporacion | INTEGER | Año de incorporación declarado | Regla SQL: anno_incorporacion BETWEEN 1900 AND 2025; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| km_totales | INTEGER | Kilometraje acumulado, no kilómetros del periodo | Regla SQL: km_totales >= 0; permite NULL | Fuera de dominio: 1; Conservar original y bandera; valor analítico nulo. |
| depot_id | INTEGER | Identificador de cochera | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| emisiones_co2_gkm | REAL | Factor de emisiones directas declarado, g CO₂/km; no incluye ciclo de vida | Regla SQL: emisiones_co2_gkm >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| en_servicio | INTEGER | Estado de servicio en la instantánea recibida | Regla SQL: en_servicio IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| combustible_inferido | INTEGER | Bandera de combustible reconstruido con correspondencia única por modelo | Regla SQL: combustible_inferido IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| anno_fabricacion_original | INTEGER | Valor original de anno_fabricacion, conservado para auditoría | Valor del CSV conservado incluso si es inválido; permite NULL | Campo derivado; regla en preparar_datos.py |
| anno_fabricacion_invalido | INTEGER | Marca de valor inválido en anno_fabricacion | Regla SQL: anno_fabricacion_invalido IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| km_totales_original | INTEGER | Valor original de km_totales, conservado para auditoría | Valor del CSV conservado incluso si es inválido; permite NULL | Campo derivado; regla en preparar_datos.py |
| km_totales_invalido | INTEGER | Marca de valor inválido en km_totales | Regla SQL: km_totales_invalido IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |


### dim_conductor

Granularidad: un conductor. 30 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| conductor_id | INTEGER | Identificador de conductor | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| nombre | TEXT | Nombre de la entidad | Texto informado; sin catálogo externo disponible; obligatorio (sin NULL) | Identificación personal: excluir de vistas públicas y rankings individuales |
| anno_incorporacion | INTEGER | Año de incorporación declarado | Regla SQL: anno_incorporacion BETWEEN 1900 AND 2024; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| antiguedad_anos | REAL | Años de antigüedad con referencia al cierre de 2024 | Regla SQL: antiguedad_anos >= 0; permite NULL | 1 nulos originales (3.333%) Nulo: 1; Calcular 2024 - anno_incorporacion, con bandera. |
| turno_habitual | TEXT | Turno asignado habitualmente | Manana (06-14h); Noche (22-06h); Partido; Tarde (14-22h); obligatorio (sin NULL) | Categoría inconsistente: 1; {'manana': 'Manana (06-14h)'} |
| depot_id | INTEGER | Identificador de cochera | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| formacion | TEXT | Formación registrada | Basica; Basica + Articulado; Basica + Electrico; Completa; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| licencia_tipo | TEXT | Categoría de permiso de conducción | Regla SQL: licencia_tipo IN ('D','D+E'); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| activo | INTEGER | Estado activo en la instantánea recibida | Regla SQL: activo IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| ausencias_2024 | INTEGER | Recuento de ausencias de 2024; unidad temporal detallada no especificada | Regla SQL: ausencias_2024 >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| antiguedad_inferida | INTEGER | Bandera de antigüedad calculada desde año incorporación | Regla SQL: antiguedad_inferida IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |


### dim_parada

Granularidad: una parada. 120 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| parada_id | INTEGER | Identificador de parada | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| nombre_parada | TEXT | Nombre de la parada | Texto informado; sin catálogo externo disponible; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| barrio | TEXT | Barrio de localización | Aeropuerto; Barrio Norte; Barrio Sur; Centro; Estacion; Hospital; Poligono; Pueblo Este; Pueblo Oeste; Universidad; Zona Comercial; obligatorio (sin NULL) | Categoría inconsistente: 2; {'centro': 'Centro', 'BARRIO NORTE': 'Barrio Norte'} |
| tipo | TEXT | Clasificación de la entidad | Regla SQL: tipo IN ('Intermedia','Intercambiador','Cabecera'); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| latitud | REAL | Coordenada geográfica norte-sur, en grados | Regla SQL: latitud BETWEEN -90 AND 90; permite NULL | 1 nulos originales (0.833%) Fuera de dominio: 1; 999 pasa a nulo, con original y bandera. Nulo original: 1; Mantener desconocido; excluir de mapas puntuales. |
| longitud | REAL | Coordenada geográfica este-oeste, en grados | Regla SQL: longitud BETWEEN -180 AND 180; permite NULL | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| accesible_silla | INTEGER | Indicación de accesibilidad para silla de ruedas | Regla SQL: accesible_silla IN (0,1); permite NULL | 1 nulos originales (0.833%) Nulo: 1; Mantener desconocido; informar cobertura. |
| marquesina | INTEGER | Disponibilidad de marquesina | Regla SQL: marquesina IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| panel_informacion | INTEGER | Disponibilidad de panel informativo | Regla SQL: panel_informacion IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| activa | INTEGER | Estado activo de la parada en la instantánea | Regla SQL: activa IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| latitud_original | REAL | Valor original de latitud, conservado para auditoría | Valor del CSV conservado incluso si es inválido; permite NULL | Campo derivado; regla en preparar_datos.py |
| latitud_invalida | INTEGER | Bandera de latitud original fuera de dominio | Regla SQL: latitud_invalida IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |


### dim_tarifa

Granularidad: un título de transporte. 9 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| tarifa_id | INTEGER | Identificador de tarifa | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| tipo_titulo | TEXT | Nombre del título de transporte | Abono Joven; Abono Jubilado; Abono Mensual; Bono 10 Viajes; Escolar; Gratuito Social; Ordinario; Turistico 1 dia; Turistico 3 dias; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| categoria | TEXT | Categoría de negocio del registro | Adulto; Escolar; Joven; Jubilado; Social; Turista; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| precio_eur | REAL | Precio nominal del título en euros; no es ingreso por viaje | Regla SQL: precio_eur >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| es_abono | INTEGER | Indica si es un abono | Regla SQL: es_abono IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| bonificado | INTEGER | Indica bonificación del título | Regla SQL: bonificado IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |


### fact_viajes

Granularidad: una expedición. 50.000 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| viaje_id | INTEGER | Identificador de expedición | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| linea_id | INTEGER | Identificador de línea | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| vehiculo_id | INTEGER | Identificador de vehículo | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| conductor_id | INTEGER | Identificador de conductor | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| parada_origen_id | INTEGER | Parada de inicio de la expedición | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| parada_destino_id | INTEGER | Parada final de la expedición | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| fecha | TEXT | Fecha del evento | Regla SQL: date(fecha) IS NOT NULL; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| anno | INTEGER | Año derivado del evento | Regla SQL: anno = CAST(strftime('%Y', fecha) AS INTEGER); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| mes | INTEGER | Mes del evento | Regla SQL: mes = CAST(strftime('%m', fecha) AS INTEGER); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| dia_semana | TEXT | Día de la semana del viaje | Friday; Monday; Saturday; Sunday; Thursday; Tuesday; Wednesday; obligatorio (sin NULL) | Etiqueta inconsistente: 30; Recalcular desde fecha con un mapa explícito. |
| es_festivo | INTEGER | Indicador de festivo según origen; no equivale a fin de semana | Regla SQL: es_festivo IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| franja_horaria | TEXT | Franja operativa del viaje; en incidencias se hereda de su viaje | Madrugada; Manana punta; Noche; Tarde; Tarde punta; Valle manana; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| hora_salida_prog | TEXT | Hora programada de salida, HH:MM | HH:MM, entre 00:00 y 23:59; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| hora_salida_real | TEXT | Hora real de salida, HH:MM | HH:MM, entre 00:00 y 23:59; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| hora_llegada_real | TEXT | Hora real de llegada, HH:MM | HH:MM, entre 00:00 y 23:59; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| retraso_salida_min | INTEGER | Salida real menos programada en minutos; admite anticipos | Minutos con signo; -99 se reconstruye; no truncar anticipos a cero; permite NULL | Código -99 incompatible con horas: 80; Recuperar diferencia real-programada en [-720,720); original y bandera. |
| duracion_real_min | INTEGER | Duración real del servicio, minutos | Regla SQL: duracion_real_min >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| pasajeros_subidos | INTEGER | Subidas registradas, no personas únicas | Regla SQL: pasajeros_subidos >= 0; permite NULL | 40 nulos originales (0.080%) Nulo: 40; Conservar observado nulo; estimación separada con mediana línea/franja y bandera. |
| ocupacion_pct | REAL | Ocupación registrada como proporción 0–1, no como 0–100 | Regla SQL: ocupacion_pct BETWEEN 0 AND 1; permite NULL | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| km_programados | REAL | Distancia programada, km | Regla SQL: km_programados >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| km_recorridos | REAL | Distancia recorrida registrada, km | Regla SQL: km_recorridos >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| viaje_completado | INTEGER | Indicador de finalización de la expedición | Regla SQL: viaje_completado IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| consumo | REAL | Cantidad de energía/combustible registrada; unidad no documentada | Regla SQL: consumo >= 0; permite NULL | 1065 nulos originales (2.130%) Nulo: 1065; Mantener nulo y medir cobertura. |
| tarifa_predominante_id | INTEGER | Título predominante, no desglose de ventas | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| pasajeros_imputados | INTEGER | Bandera que identifica estimación en pasajeros_estimados | Regla SQL: pasajeros_imputados IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| pasajeros_estimados | REAL | Pasajeros observados o mediana línea/franja si faltan; solo sensibilidad | Regla SQL: pasajeros_estimados >= 0; permite NULL | Campo derivado; regla en preparar_datos.py |
| consumo_ausente | INTEGER | Bandera de consumo desconocido | Regla SQL: consumo_ausente IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| retraso_salida_min_original | INTEGER | Valor original de retraso_salida_min, conservado para auditoría | Valor del CSV conservado incluso si es inválido; permite NULL | Campo derivado; regla en preparar_datos.py |
| retraso_corregido | INTEGER | Bandera de retraso -99 reconstruido desde horas | Regla SQL: retraso_corregido IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| es_retrasado | INTEGER | Salida con más de cinco minutos de retraso | Regla SQL: es_retrasado IN (0,1); permite NULL | Campo derivado; regla en preparar_datos.py |
| en_periodo | INTEGER | Fecha del hecho dentro de 2022-01-01 y 2024-12-31 | Regla SQL: en_periodo IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| vehiculo_previo_incorporacion | INTEGER | Bandera de viaje anterior al año incorporación declarado del vehículo | Regla SQL: vehiculo_previo_incorporacion IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| franja_id | INTEGER | Clave de dimensión franja; 0 significa Sin franja | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| fecha_franja_id | TEXT | Clave única fecha ISO + separador + franja_id | Fecha ISO + franja; existe en dim_calendario_franja; obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |


### fact_incidencias

Granularidad: una incidencia. 4.000 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| incidencia_id | INTEGER | Identificador de incidencia | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| viaje_id | INTEGER | Identificador de expedición | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| vehiculo_id | INTEGER | Identificador de vehículo | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| conductor_id | INTEGER | Identificador de conductor | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| linea_id | INTEGER | Identificador de línea | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| fecha | TEXT | Fecha del evento | Regla SQL: date(fecha) IS NOT NULL; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| anno | INTEGER | Año derivado del evento | Regla SQL: anno = CAST(strftime('%Y', fecha) AS INTEGER); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| mes | INTEGER | Mes del evento | Regla SQL: mes = CAST(strftime('%m', fecha) AS INTEGER); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| hora_incidencia | TEXT | Hora de registro de la incidencia, HH:MM | HH:MM, entre 00:00 y 23:59; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| tipo_incidencia | TEXT | Clasificación detallada del evento | Accidente grave; Accidente leve; Averia mecanica; Condiciones meteo; Fallo climatizacion; Fallo electrico; Huelga parcial; Obras calzada; Pasajero enfermo; Pinchazo; Retencion trafico; Vandalismo; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| categoria | TEXT | Categoría de negocio del registro | Externo; Operacional; Seguridad; Servicio; Vehiculo; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| severidad | TEXT | Grado cualitativo de severidad | Regla SQL: severidad IN ('Baja','Media','Alta','Critica'); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| requiere_retirada | INTEGER | Indicador de retirada del vehículo | Regla SQL: requiere_retirada IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| duracion_resolucion_min | INTEGER | Tiempo registrado de resolución, minutos | Regla SQL: duracion_resolucion_min >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| vehiculo_sustituto | INTEGER | Indicador de uso de vehículo sustituto | Regla SQL: vehiculo_sustituto IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| coste_estimado_eur | REAL | Estimación del coste de incidencia, euros; no factura liquidada | Regla SQL: coste_estimado_eur >= 0; permite NULL | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| en_periodo | INTEGER | Fecha del hecho dentro de 2022-01-01 y 2024-12-31 | Regla SQL: en_periodo IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| franja_horaria | TEXT | Franja operativa del viaje; en incidencias se hereda de su viaje | Madrugada; Manana punta; Noche; Tarde; Tarde punta; Valle manana; obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| franja_id | INTEGER | Clave de dimensión franja; 0 significa Sin franja | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| fecha_franja_id | TEXT | Clave única fecha ISO + separador + franja_id | Fecha ISO + franja; existe en dim_calendario_franja; obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |


### fact_mantenimiento

Granularidad: una intervención. 876 filas.

| Campo | Tipo | Descripción | Valores válidos o rango esperado | Observaciones de calidad |
| --- | --- | --- | --- | --- |
| mantenimiento_id | INTEGER | Identificador de intervención | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| vehiculo_id | INTEGER | Identificador de vehículo | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| depot_id | INTEGER | Identificador de cochera | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| fecha_entrada | TEXT | Fecha de inicio de intervención; determina su periodo de reporting | Regla SQL: date(fecha_entrada) IS NOT NULL; obligatorio (sin NULL) | Fuera de periodo: 47; Conservar filas; excluir del reporting 2022-2024 por fecha de entrada. |
| fecha_salida | TEXT | Fecha de cierre de intervención | Regla SQL: date(fecha_salida) IS NOT NULL AND fecha_salida >= fecha_entrada; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| anno | INTEGER | Año derivado del evento | Regla SQL: anno = CAST(strftime('%Y', fecha_entrada) AS INTEGER); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| mes | INTEGER | Mes del evento | Regla SQL: mes = CAST(strftime('%m', fecha_entrada) AS INTEGER); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| tipo_mantenimiento | TEXT | Intervención concreta realizada | Cambio aceite; Cambio neumaticos; Carroceria y pintura; ITV e Inspeccion; Reparacion clima; Reparacion frenos; Reparacion motor; Revision bateria; Revision periodica; Sistema electrico; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| categoria | TEXT | Categoría de negocio del registro | Regla SQL: categoria IN ('Preventivo','Correctivo','Legal','Estetico'); permite NULL | 15 nulos originales (1.712%) Nulo: 15; Inferir solo con categoría única por tipo_mantenimiento; marcar categoria_inferida. |
| es_correctivo | INTEGER | Indicador de mantenimiento correctivo | Regla SQL: es_correctivo IN (0,1); obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| dias_fuera_servicio | INTEGER | Duración registrada de inmovilización; puede solaparse con otras intervenciones | Regla SQL: dias_fuera_servicio >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| km_en_revision | INTEGER | Kilometraje registrado en la intervención | Regla SQL: km_en_revision >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| coste_eur | REAL | Importe observado válido de mantenimiento, euros | Regla SQL: coste_eur >= 0; permite NULL | Importe negativo sin tipo de abono: 25; Mantener registro; importe analítico nulo, original y bandera. Coste observado válido. |
| proveedor | TEXT | Proveedor del mantenimiento | FlotaService; ManteAuto S.L.; Taller Oficial MAN; Taller Oficial Mercedes; TallerBus Norte; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| garantia_meses | INTEGER | Meses de garantía registrados | Regla SQL: garantia_meses >= 0; obligatorio (sin NULL) | Sin incidencia específica en las comprobaciones aplicadas; no implica certificación de origen |
| categoria_inferida | INTEGER | Bandera de categoría reconstruida por tipo de mantenimiento | Regla SQL: categoria_inferida IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| coste_eur_original | REAL | Valor original de coste_eur, conservado para auditoría | Valor del CSV conservado incluso si es inválido; permite NULL | Campo derivado; regla en preparar_datos.py |
| coste_invalido | INTEGER | Bandera de importe original negativo sin naturaleza acreditada | Regla SQL: coste_invalido IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| en_periodo | INTEGER | Fecha del hecho dentro de 2022-01-01 y 2024-12-31 | Regla SQL: en_periodo IN (0,1); obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| franja_id | INTEGER | Clave de dimensión franja; 0 significa Sin franja | Entero identificador; unicidad/referencia según 02_sql.sql; obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |
| fecha_franja_id | TEXT | Clave única fecha ISO + separador + franja_id | Fecha ISO + franja; existe en dim_calendario_franja; obligatorio (sin NULL) | Campo derivado; regla en preparar_datos.py |


## 3. Registro de decisiones de calidad

La frecuencia cuenta filas afectadas antes de limpiar. Las entradas pueden referirse a una misma fila y no deben sumarse como registros únicos. Resolver significa aplicar un tratamiento auditable, que puede ser conservar un desconocido.

| Tabla | Campo | Problema | Filas | Decisión | Justificación |
| --- | --- | --- | --- | --- | --- |
| dim_vehiculo | combustible | Categoría inconsistente | 1 | {'diesel': 'Diesel'} | Unificar etiquetas equivalentes; no cambia su significado. |
| dim_conductor | turno_habitual | Categoría inconsistente | 1 | {'manana': 'Manana (06-14h)'} | Unificar etiquetas equivalentes; no cambia su significado. |
| dim_parada | barrio | Categoría inconsistente | 2 | {'centro': 'Centro', 'BARRIO NORTE': 'Barrio Norte'} | Unificar etiquetas equivalentes; no cambia su significado. |
| fact_viajes | dia_semana | Etiqueta inconsistente | 30 | Recalcular desde fecha con un mapa explícito. | Fecha validada es la fuente; evita etiquetas duplicadas y depende menos del idioma del sistema. |
| dim_vehiculo | combustible | Nulo | 1 | Inferir solo con categoría única por modelo; marcar combustible_inferido. | Correspondencia unívoca observada; una categoría ambigua quedaría nula. |
| fact_mantenimiento | categoria | Nulo | 15 | Inferir solo con categoría única por tipo_mantenimiento; marcar categoria_inferida. | Correspondencia unívoca observada; una categoría ambigua quedaría nula. |
| dim_conductor | antiguedad_anos | Nulo | 1 | Calcular 2024 - anno_incorporacion, con bandera. | Antigüedad en años enteros al cierre; coincide con los valores informados. |
| dim_vehiculo | anno_fabricacion | Fuera de dominio | 1 | Conservar original y bandera; valor analítico nulo. | No existe evidencia para reconstruir el valor real. |
| dim_vehiculo | km_totales | Fuera de dominio | 1 | Conservar original y bandera; valor analítico nulo. | No existe evidencia para reconstruir el valor real. |
| dim_parada | latitud | Fuera de dominio | 1 | 999 pasa a nulo, con original y bandera. | Una latitud debe estar entre -90 y 90 grados. |
| dim_parada | latitud | Nulo original | 1 | Mantener desconocido; excluir de mapas puntuales. | Una mediana de barrio inventaría una ubicación. |
| dim_parada | accesible_silla | Nulo | 1 | Mantener desconocido; informar cobertura. | La accesibilidad requiere comprobación física, no imputación por mayoría. |
| fact_viajes | pasajeros_subidos | Nulo | 40 | Conservar observado nulo; estimación separada con mediana línea/franja y bandera. | El KPI principal suma pasajeros observados; estimados solo para sensibilidad. |
| fact_viajes | consumo | Nulo | 1065 | Mantener nulo y medir cobertura. | No hay unidad documentada ni evidencia para imputar. No comparar tecnologías con una suma de consumo. |
| fact_viajes | retraso_salida_min | Código -99 incompatible con horas | 80 | Recuperar diferencia real-programada en [-720,720); original y bandera. | Las otras 49.920 filas concuerdan con la fórmula. Supuesto: desviación menor de 12 horas. |
| fact_mantenimiento | coste_eur | Importe negativo sin tipo de abono | 25 | Mantener registro; importe analítico nulo, original y bandera. Coste observado válido. | No hay evidencia de abono ni del importe correcto. El KPI informa cobertura, sin presentar estimaciones como coste real. |
| fact_mantenimiento | fecha_entrada | Fuera de periodo | 47 | Conservar filas; excluir del reporting 2022-2024 por fecha de entrada. | Cierre común y reproducible; no se trasladan costes a 2024. |
| fact_viajes | fecha / anno_incorporacion vehículo | Cronología de dimensión incompatible | 7941 | Marcar y conservar viajes; no usar año incorporación para disponibilidad histórica. | La dimensión es una instantánea sintética, no un historial fiable de altas; requiere aclaración de origen. |



## 4. Contrato de KPIs

Todas las medidas usan 2022–2024 inclusive y los filtros seleccionados. El mantenimiento
se atribuye a fecha de entrada. Cada indicador se calcula en el hecho correspondiente,
sin unir filas de viajes con múltiples incidencias o intervenciones. Los promedios se
recalculan desde registros, no promediando medias de grupos de distinto tamaño.

| KPI | Fórmula exacta | Fuente | Exclusiones y unidad | Responsable de validación |
| --- | --- | --- | --- | --- |
| Expediciones | COUNT(viaje_id) | fact_viajes.viaje_id, fecha | Incluye expediciones no completadas, que existen en el registro | Operaciones |
| Pasajeros observados | SUM(pasajeros_subidos) | fact_viajes.pasajeros_subidos | Excluye NULL, nunca los sustituye por cero; son subidas, no usuarios únicos | Planificación |
| Cobertura de pasajeros | 100 × COUNT(pasajeros_subidos) / COUNT(viaje_id) | fact_viajes | Porcentaje de expediciones con recuento; NULL si denominador cero | Calidad del dato |
| Salidas retrasadas | 100 × SUM(CASE WHEN retraso_salida_min > 5 THEN 1 ELSE 0 END) / COUNT(retraso_salida_min) | fact_viajes.retraso_salida_min | Incluye correcciones contrastadas con horas; >5 estricto; NULL si no hay valores válidos | Operaciones |
| Retraso medio | AVG(retraso_salida_min) | fact_viajes.retraso_salida_min | Minutos; incluye anticipos válidos, excluye NULL | Operaciones |
| Ocupación media | 100 × AVG(ocupacion_pct) | fact_viajes.ocupacion_pct | Media por expedición; no ponderada por distancia ni capacidad | Planificación |
| Incidencias por 1.000 viajes | 1000 × COUNT(incidencia_id) / COUNT(viaje_id) | fact_incidencias y fact_viajes agregadas con mismo año, línea y combustible | Cuenta eventos, no viajes afectados; varios eventos por viaje son posibles; NULL sin viajes | Operaciones |
| Intervenciones | COUNT(mantenimiento_id) | fact_mantenimiento.fecha_entrada, mantenimiento_id | Incluye registros cuyo coste es desconocido | Taller |
| Coste observado válido | SUM(coste_eur) | fact_mantenimiento.coste_eur, fecha_entrada | EUR; 23 importes excluidos en 2022–2024; es subtotal válido, no coste total completo | Taller y Finanzas |
| Cobertura del coste | 100 × COUNT(coste_eur) / COUNT(mantenimiento_id) | fact_mantenimiento | Porcentaje; no confundir coste NULL con intervención sin coste | Taller |
| Coste medio válido | SUM(coste_eur) / COUNT(coste_eur) | fact_mantenimiento | EUR/intervención con importe conocido; NULL sin costes válidos | Taller y Finanzas |
| Coste por 1.000 km | 1000 × SUM(coste_eur) / SUM(km_recorridos) | Mantenimiento y viajes agregados primero por vehículo/combustible y periodo | EUR/1.000 km; exposición registrada, no actividad total certificada; sin denominador positivo devuelve NULL | Flota |

**Medida de sensibilidad, fuera de titulares:** SUM(pasajeros_estimados) utiliza medianas
línea/franja para 40 valores ausentes. El informe mantiene el total observado como referencia.
El consumo no produce un KPI comparativo entre tecnologías hasta confirmar sus unidades.
El precio del título predominante no permite calcular recaudación real.

## 5. Modelo temporal y cardinalidades

Cada hecho conserva su granularidad y se conecta a dimensiones por claves muchos-a-uno.
Vehículo y conductor se relacionan con cochera. Paradas tiene dos roles en viajes
(origen y destino), con alias distintos. No se unen hechos entre sí para sumar medidas.

`dim_calendario` tiene una fila por fecha de 2022-01-01 a 2025-12-31 y es la referencia
temporal oficial: `fecha`, `anno`, `mes`, `mes_nombre`, `trimestre`, `semana_iso`,
`anno_iso`, `dia_semana` y `es_fin_semana`. Año ISO acompaña semana para evitar
mezclar semanas que cruzan año natural. Mes se ordena por su número.

Una fecha puede tener varias franjas. Duplicar fechas y relacionar solo por fecha
provocaría una relación muchos-a-muchos. Se entrega `dim_franja` y la dimensión
`dim_calendario_franja`, cuyo grano es fecha × franja y cuya clave única es
`fecha_franja_id`. Esta última contiene todos los atributos de calendario y franja,
permitiendo relacionar cada hecho por una clave muchos-a-uno. Mantenimiento usa
`Sin franja` porque no tiene una hora de intervención. Incidencias hereda la franja
del viaje asociado, por lo que significa franja de servicio, no franja de reloj del evento.

Tableau reconoce `fecha` como Date y ofrece jerarquías de fecha. No dispone de la
misma orden «Marcar como tabla de fechas» de Power BI: el carácter oficial se
establece en el modelo y su documentación, manteniendo una clave temporal única.
Un filtro de línea no debe aplicarse a mantenimiento: la intervención no tiene línea
atribuible. La interfaz debe hacer explícito ese alcance. Filtros comunes de año y
combustible sí tienen interpretación consistente entre hechos.

## 6. Controles, trazabilidad y privacidad

- Validación de PK, FK, tipos, rangos y coherencia incidencia-viaje antes de publicar resultados.
- Originales inmutables, banderas y valores originales de las correcciones numéricas.
- CSV limpio generado siempre desde crudos, sin encadenar correcciones sobre salidas previas.
- SQLite se construye en un archivo temporal, comprueba integridad y sustituye la salida solo al completar.
- No se borran extremos por IQR: el criterio estadístico identifica candidatos a revisión.
- Nombres de conductores se conservan en la entrega local académica, pero no se incluyen en gráficos.
  Para publicar, se omitirían esos nombres y las matrículas o se pseudonimizarían según necesidad.
- Tableau Public permite publicar en Internet, pero este proyecto se entrega como archivo local;
  no se autoriza ni se necesita subir sus datos a un servidor público.
- No hay historial fiable de altas/bajas ni intervalos de inmovilización depurados de solapamientos:
  no se afirma disponibilidad histórica de flota ni causalidad entre combustible y averías.

## 7. Limitaciones que requieren validación de origen

Los 7.941 viajes previos al año de incorporación declarado indican incompatibilidad
entre hechos y la instantánea de flota. Se mantienen con bandera para evitar alterar
el universo de expediciones sin conocer el error de origen. Los datos describen una
operadora ficticia y no acreditan cobertura completa del servicio real. Los costes
excluidos no pueden tratarse como cero. Las coordenadas y accesibilidad desconocidas
necesitan verificación, y las unidades de consumo necesitan un diccionario de origen.
