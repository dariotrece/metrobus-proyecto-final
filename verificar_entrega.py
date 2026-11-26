"""Comprobaciones básicas del análisis. Uso: python verificar_entrega.py"""
from pathlib import Path
import json
import math
import sqlite3
import pandas as pd
from src.preparar_datos import CLAVES, validar_relaciones

ROOT = Path(__file__).resolve().parent


def main():
    tablas = {}
    for nombre, clave in CLAVES.items():
        original = pd.read_csv(ROOT / "data" / f"{nombre}.csv")
        limpio = pd.read_csv(ROOT / "data_clean" / f"{nombre}.csv")
        assert len(limpio) == len(original), f"Han cambiado las filas de {nombre}"
        assert limpio[clave].notna().all(), f"Clave nula en {nombre}"
        assert limpio[clave].is_unique, f"Clave repetida en {nombre}"
        tablas[nombre] = limpio
    assert validar_relaciones(tablas)["incumplimientos"].sum() == 0
    print("OK: filas conservadas, claves únicas y referencias completas.")

    ruta = ROOT / "resultados/metrobus.db"
    with sqlite3.connect(f"file:{ruta}?mode=ro", uri=True) as con:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
        for nombre, limpio in tablas.items():
            cargado = pd.read_sql_query(f'SELECT * FROM "{nombre}"', con)
            pd.testing.assert_frame_equal(limpio, cargado[limpio.columns], check_dtype=False)
    print("OK: SQLite contiene los mismos datos que los CSV limpios.")

    viajes = tablas["fact_viajes"]
    mantenimiento = tablas["fact_mantenimiento"]
    periodo = mantenimiento[mantenimiento["en_periodo"]]
    # Valores de referencia comprobados para esta versión del dataset.
    assert viajes["pasajeros_subidos"].isna().sum() == 40
    assert viajes["pasajeros_subidos"].sum() == 3061744
    assert viajes["retraso_corregido"].sum() == 80
    assert math.isclose(viajes["es_retrasado"].mean() * 100, 24.632)
    assert len(periodo) == 829
    assert periodo["coste_eur"].isna().sum() == 23
    assert math.isclose(periodo["coste_eur"].sum(), 632808.45)
    print("OK: pasajeros, retrasos y mantenimiento mantienen los totales comprobados.")
    resultado = {"estado": "OK", "controles": ["filas y claves", "CSV frente a SQLite", "KPIs de referencia"]}
    (ROOT / "resultados/verificacion_basica.json").write_text(json.dumps(resultado, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
