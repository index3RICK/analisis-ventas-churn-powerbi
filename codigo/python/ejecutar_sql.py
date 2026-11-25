"""
ejecutar_sql.py
===============
Carga las ventas en una base SQLite EN MEMORIA, ejecuta
sql/churn_por_categoria.sql y (opcionalmente) lo compara con el cálculo en
pandas. Sirve para demostrar que tres herramientas distintas (DAX, pandas y
SQL) llegan al mismo resultado.

Uso (desde la raíz del repositorio):
    python python/ejecutar_sql.py
    python python/ejecutar_sql.py --fecha-ref 2025-09-05 --umbral 90 --comparar
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cargar_datos import RUTA_POR_DEFECTO, agregar_argumentos_datos, cargar_ventas  # noqa: E402
from churn import fecha_ref_por_defecto, resumen_churn  # noqa: E402

RUTA_SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sql", "churn_por_categoria.sql")


def ejecutar(ventas: pd.DataFrame, fecha_ref: pd.Timestamp, umbral: int) -> pd.DataFrame:
    """Ejecuta el .sql contra una base en memoria y devuelve el resultado."""
    tabla = ventas.copy()
    # SQLite no tiene tipo fecha: guardamos 'AAAA-MM-DD' como texto.
    tabla["Fecha"] = tabla["Fecha"].dt.strftime("%Y-%m-%d")

    conexion = sqlite3.connect(":memory:")
    try:
        tabla.to_sql("ventas", conexion, index=False)
        with open(RUTA_SQL, encoding="utf-8") as archivo:
            consulta = archivo.read()
        return pd.read_sql_query(
            consulta, conexion, params={"fecha_ref": fecha_ref.strftime("%Y-%m-%d"), "umbral": umbral}
        )
    finally:
        conexion.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Ejecuta la consulta SQL de churn sobre SQLite en memoria.")
    parser.add_argument("--ruta", default=RUTA_POR_DEFECTO)
    agregar_argumentos_datos(parser)
    parser.add_argument("--fecha-ref", default=None, help="AAAA-MM-DD (por defecto: última venta).")
    parser.add_argument("--umbral", type=int, default=90)
    parser.add_argument("--comparar", action="store_true", help="Compara contra el cálculo en pandas.")
    args = parser.parse_args()

    ventas = cargar_ventas(args.ruta, iva=args.iva, corregir_agencias=args.corregir_agencias)
    fecha_ref = pd.Timestamp(args.fecha_ref) if args.fecha_ref else fecha_ref_por_defecto(ventas)

    resultado = ejecutar(ventas, fecha_ref, args.umbral)
    with pd.option_context("display.max_rows", None, "display.width", 120):
        print(resultado.to_string(index=False))

    if args.comparar:
        # SQL replica el modo "correcto" (a la fecha), así que se compara con ese.
        esperado = resumen_churn(ventas, fecha_ref, args.umbral, modo="correcto", por_categoria=True)
        unido = resultado.merge(esperado, on="categoria", suffixes=("_sql", "_pandas"))
        iguales = (
            (unido["clientes_totales_sql"] == unido["clientes_totales_pandas"]).all()
            and (unido["clientes_con_churn_sql"] == unido["clientes_con_churn_pandas"]).all()
            and len(unido) == len(resultado) == len(esperado)
        )
        print("-" * 70)
        print("Comparación SQL vs pandas:", "COINCIDEN en todas las categorías" if iguales else "HAY DIFERENCIAS")
        return 0 if iguales else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
