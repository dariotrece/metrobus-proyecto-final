# Cuadro de mando de MetroBus en Tableau

## Abrir y navegar

Abre `04_dashboard.twbx` con Tableau Public Desktop o Tableau Desktop (2025.1 o posterior). El paquete incorpora las extracciones Hyper y los CSV necesarios y funciona de forma local: no requiere una cuenta para consultar el archivo ni publicar los datos.

Las pestañas de dashboard son **01 · Demanda**, **02 · Servicio** y **03 · Mantenimiento**. Cada página contiene tres indicadores y dos gráficos. Las hojas auxiliares se conservan para que se pueda revisar cómo está construido cada gráfico.

| Página | Pregunta | Contenido |
|---|---|---|
| Demanda | ¿Dónde reforzar el servicio? | Expediciones, pasajeros registrados, cobertura de pasajeros, demanda por línea y franja |
| Servicio | ¿Dónde se concentra el retraso? | Porcentaje de salidas con más de 5 minutos de retraso, ocupación media, incidencias por 1.000 viajes, retraso por franja y categorías de incidencia |
| Mantenimiento | ¿Cómo evoluciona el mantenimiento? | Intervenciones, coste observado válido, cobertura de costes, evolución anual y coste medio por tecnología |

## Selección sincronizada

Los controles **Año**, **Mes**, **Combustible** y **Línea** son parámetros del libro, por lo que conservan su valor al cambiar de página. `0` significa todos los años o todos los meses. Para restablecer la vista global, selecciona año `0`, mes `0`, combustible `Todos` y línea `Todas`.

La línea se aplica a viajes e incidencias. **No se aplica a mantenimiento**: el dataset no asigna cada intervención a una línea y un vehículo puede circular por varias. Inventar esa relación atribuiría costes a servicios sin evidencia. El año y el mes de mantenimiento corresponden a `fecha_entrada`.

Los filtros no cambian el cierre del análisis: los indicadores se limitan a 2022–2024. Los registros de enero de 2025 siguen disponibles en el modelo para trazabilidad.

## Modelo de datos y granularidad

El libro contiene tres fuentes en estrella: **Viajes**, **Incidencias** y **Mantenimiento**. Cada fuente mantiene la granularidad de su hecho y usa relaciones lógicas de muchos a uno con las dimensiones que le corresponden. Las claves únicas y la integridad referencial se verifican antes de empaquetar el libro.

- Viajes: línea, vehículo, conductor, parada de origen, parada de destino, tarifa, cochera del vehículo y calendario-franja.
- Incidencias: línea, vehículo, conductor y calendario-franja.
- Mantenimiento: vehículo, cochera y calendario-franja.

Las dimensiones compartidas proceden de los mismos archivos limpios. Las selecciones globales las coordinan entre fuentes. No se unen físicamente las tres tablas de hechos: un viaje con varias incidencias no debe multiplicar sus pasajeros.

Para el indicador de incidencias por 1.000 viajes se agrega previamente el número de incidencias de cada viaje y se añade como medida a la fuente Viajes. La operación conserva exactamente una fila por expedición y permite que numerador y denominador reciban la misma selección de fecha, línea y combustible.

## Dimensión temporal oficial

`dim_calendario.csv` tiene una fila por fecha, con año, mes, trimestre, semana ISO y año ISO. `dim_franja.csv` contiene las franjas. Como una fecha tiene varias franjas, se usa `dim_calendario_franja.csv` en Tableau: su clave única es `fecha_franja_id`, combinación de fecha y franja. Así se incluyen todas las columnas temporales que exige el enunciado sin relacionar una fecha contra varias filas y multiplicar medidas.

En mantenimiento la franja es `Sin franja`: no se conoce una hora operativa comparable a la del viaje. La fecha se declara como tipo `date`. Tableau no tiene el botón de Power BI «Marcar como tabla de fechas»; la dimensión oficial queda definida mediante su clave, su tipo de fecha, las relaciones y esta documentación.

## Interpretación de las métricas

Las fórmulas completas, fuentes, exclusiones y responsables están en `03_gobierno.md`. En el cuadro de mando:

- Pasajeros significa **subidas registradas**, no personas únicas ni demanda total de la ciudad. Se excluyen de la suma los valores ausentes y se muestra su cobertura.
- Un viaje retrasado es aquel cuya salida se retrasa **más de cinco minutos**. Los adelantos válidos se conservan. Los 80 valores centinela `-99` se recuperan a partir de las horas programada y real y conservan un indicador de corrección.
- Incidencias por 1.000 viajes cuenta eventos. Un mismo viaje puede tener más de una incidencia.
- Los costes negativos de mantenimiento no se transforman en costes reales inventados: quedan como ausentes en el campo válido; el valor original y la marca de calidad se conservan. La tarjeta de cobertura muestra qué proporción tiene coste válido.
- El coste medio por tecnología es una comparación descriptiva por intervención, no una demostración de que un combustible sea más barato. Cambian edad de flota, tipo de trabajo y uso; faltan precio de compra, energía e infraestructura.

## Abrir, editar y comprobar

Abre `04_dashboard.twbx` directamente en Tableau Public Desktop o Tableau Desktop. El paquete contiene el libro editable y sus extracciones; no necesita scripts de generación ni la carpeta `tableau/`. Las hojas, campos calculados, relaciones y dashboards se pueden editar desde Tableau. Guarda los cambios como un nuevo archivo TWBX local.

`python ejecutar.py` reconstruye los CSV limpios y SQLite. Si modificas los datos de origen, tendrás que actualizar también las fuentes de Tableau: el TWBX entregado representa la versión del dataset analizada. Revisa las relaciones y los campos derivados al sustituir una fuente.

Para comprobar el libro, comienza sin filtros; cambia año a 2024 y visita las tres páginas. Los parámetros deben conservarse. La selección de línea se aplica a viajes e incidencias, pero no a mantenimiento. Contrasta los indicadores con las consultas SQL exportadas en `resultados/consultas_sql/`.

El libro se abrió correctamente en Tableau Public 2025.1.3; la página de mantenimiento mostró los totales reconciliados con SQL. El alcance de la revisión está en `REVISION_ENTREGA.md`.

## Privacidad y alcance

Los archivos incluidos dentro del paquete Tableau usan etiquetas de conductor y vehículo en lugar de nombres y matrículas. Los CSV originales se conservan en `data/` para la entrega académica. El libro no se ha publicado en Tableau Public. Forma parte de la entrega académica y del repositorio privado del proyecto.

La documentación oficial de [cardinalidad](https://help.tableau.com/current/pro/desktop/en-us/cardinality_and_ri.htm) explica la distinción entre unicidad de claves e integridad referencial. Las relaciones configuradas en el libro se basan en ambas comprobaciones sobre este dataset.
