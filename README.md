# MetroBus Analytics

**Darío Pérez Lorenzo · Proyecto final de Data Analytics**

Análisis de demanda, puntualidad y mantenimiento de MetroBus durante 2022–2024. Los nueve CSV sintéticos originales están en `data/` y no se sobrescriben.

## Contenido

- `01_eda.ipynb`: exploración ejecutada, nulos, outliers, gráficos y conclusiones.
- `02_sql.sql`: nueve tablas con claves y restricciones; doce consultas de negocio.
- `03_gobierno.md`: diccionario, dieciocho decisiones de limpieza y doce KPIs.
- `04_dashboard.twbx`: tres páginas de Tableau con los datos incluidos.
- `05_presentacion.pdf`: presentación ejecutiva de ocho diapositivas.

`src/preparar_datos.py` contiene la limpieza; `src/cargar_sqlite.py` crea la base y ejecuta las consultas. `data_clean/` guarda los datos preparados y `resultados/`, la base SQLite, consultas y controles. La guía de Tableau y la revisión de requisitos están en `docs/`.

## Cómo reproducirlo

Entorno comprobado: Python 3.13.5, pandas 3.0.3, NumPy 2.5.0, Matplotlib 3.11.1, SQLite 3 y Tableau Public 2025.1.3. Las versiones Python están en `requirements.txt`.

Desde esta carpeta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Fase 1:** abre `01_eda.ipynb` en VS Code con soporte Jupyter, selecciona el Python de `.venv` como kernel y pulsa «Ejecutar todo». El código y las explicaciones se editan directamente en el notebook.

**Limpieza y fase 2:**

```bash
python ejecutar.py
```

Este comando prepara los CSV, crea `resultados/metrobus.db` mediante el DDL de `02_sql.sql`, inserta los datos con `sqlite3` y exporta las doce consultas. Termina comprobando filas, claves, coincidencia CSV/SQL y KPIs. Para repetir solo esas comprobaciones: `python verificar_entrega.py`.

Abre el TWBX en Tableau para explorar o editar las visualizaciones. Los documentos y el dashboard no se regeneran al ejecutar la limpieza. Si cambias los datos originales, también tendrás que actualizar esos entregables y revisar los valores de referencia de las comprobaciones.

## Decisión de limpieza

Los cuarenta recuentos de pasajeros ausentes permanecen nulos en el KPI observado; su estimación se guarda aparte. Los costes negativos se excluyen del subtotal válido y se informa su cobertura. Los ochenta retrasos `-99` se reconstruyen desde las horas, conservando originales y anticipos legítimos.

## Hallazgo principal

Las franjas punta concentran el 63,06 % de las subidas registradas en el 40,34 % de los viajes, lo que justifica evaluar refuerzos. El coste válido de mantenimiento crece un 52,67 % entre 2022 y 2024, acompañado de más intervenciones con coste conocido y menor coste medio; no demuestra por sí solo pérdida de eficiencia.

## Uso de IA

Parte del código y de los documentos fue generada y revisada con OpenAI Codex. También se utilizó esta ayuda para construir el archivo Tableau y contrastar los resultados. La entrega incluye el análisis ejecutable y los artefactos finales; no incluye las herramientas auxiliares de generación.
