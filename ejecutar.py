"""Prepara los datos, carga SQLite y comprueba los resultados.

Uso: python ejecutar.py
El notebook se ejecuta desde Jupyter o VS Code; no se sobrescribe aquí.
"""
from src.preparar_datos import main as preparar_datos
from src.cargar_sqlite import cargar_base
from verificar_entrega import main as verificar


def main():
    print("1. Limpiar los CSV originales")
    preparar_datos()
    print("2. Crear SQLite y ejecutar las consultas")
    cargar_base()
    print("3. Comprobar filas, claves y totales")
    verificar()
    print("Proceso terminado. El notebook y el dashboard se abren por separado.")


if __name__ == "__main__":
    main()
