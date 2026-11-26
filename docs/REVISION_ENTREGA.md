# Revisión de la entrega

| Requisito | Evidencia |
| --- | --- |
| Datos originales | Nueve CSV, 55.093 filas y hashes SHA-256 en resultados/calidad_fuentes.csv |
| EDA | Notebook ejecutado: nueve tablas, nulos y patrones, outliers, seis figuras y conclusiones |
| SQL | Nueve tablas con PK/FK/CHECK, carga Python y doce consultas comentadas |
| Gobierno | Nueve diccionarios, dieciocho decisiones de calidad y doce KPIs |
| Tableau | TWBX con tres fuentes de hechos, quince relaciones muchos a uno, quince hojas y tres dashboards |
| Tiempo | Calendario con año, mes, trimestre, semana ISO y franja; claves únicas |
| Navegación y selección | Pestañas de dashboard y parámetros compartidos; línea no aplica a mantenimiento |
| Presentación | Ocho diapositivas con problema, datos, tres hallazgos, recomendaciones, limitaciones y próximos pasos |
| Reproducibilidad | Notebook directo; python ejecutar.py para limpieza, SQL y comprobaciones |
| README | Menos de quinientas palabras, instrucciones, stack, decisiones, hallazgo y declaración de IA |

## Validación

El proceso de limpieza y SQL se ejecuta desde esta carpeta. Comprueba filas, unicidad, referencias, igualdad CSV/SQLite y cifras de pasajeros, retrasos y mantenimiento. El resultado se registra en `resultados/verificacion_basica.json`.

Una auditoría adicional previa a la entrega verificó las restricciones SQL con datos inválidos en una copia temporal, las seis figuras del notebook, las ocho páginas del PDF y la estructura y datos del TWBX. Sus informes se incluyen en `resultados/`; las herramientas avanzadas utilizadas para esa auditoría se conservan fuera de la entrega. La presentación fue renderizada y revisada visualmente.

El TWBX se abrió correctamente en Tableau Public 2025.1.3. La página de mantenimiento mostró 829 intervenciones, 632.808,45 EUR y cobertura del 97,23 %, coincidentes con SQL. La revisión no incluye una prueba interactiva exhaustiva de todas las combinaciones de filtros. `GUIA_TABLEAU.md` explica cómo realizar una comprobación manual de navegación y selección.

La selección de archivos para esta entrega no altera los datos ni los resultados: se conservan el notebook ejecutado, el SQL, el documento de gobierno, el dashboard completo y la presentación. Los generadores auxiliares no son necesarios para abrir los entregables ni reproducir las fases 1 y 2.
