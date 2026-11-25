"""
validar_churn.py
================
Recalcula churn y retención FUERA de Power BI para comprobar que las medidas
DAX están bien. Si los números de este script y los del reporte coinciden
(misma fecha de referencia y mismo umbral), las medidas son correctas.

Ejemplos de uso (desde la raíz del repositorio):

    # Total general con la última venta como fecha de referencia, umbral 90
    python python/validar_churn.py

    # Tabla por categoría (como el panel Abandono de Clientes)
    python python/validar_churn.py --por-categoria

    # Reproducir una captura con otra fecha de corte
    python python/validar_churn.py --fecha-ref 2025-10-02 --por-categoria

    # Sensibilidad: ¿cómo cambia el churn según el umbral?
    python python/validar_churn.py --sensibilidad 30,60,90,180

    # Validar la versión mejorada del DAX (churn PY "a la fecha")
    python python/validar_churn.py --modo correcto --por-categoria
"""

from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

# Permite ejecutar el script desde cualquier carpeta.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cargar_datos import RUTA_POR_DEFECTO, agregar_argumentos_datos, cargar_ventas  # noqa: E402
from churn import (  # noqa: E402
    fecha_ref_por_defecto,
    resumen_churn,
    restar_meses,
    tabla_abandono,
)


def formatear_pct(tabla: pd.DataFrame) -> pd.DataFrame:
    """Muestra columnas de porcentaje con 2 decimales, como Power BI."""
    salida = tabla.copy()
    for columna in salida.columns:
        if columna.endswith("%") or columna.endswith("%_PY"):
            salida[columna] = (salida[columna] * 100).map(
                lambda x: "" if pd.isna(x) else f"{x:,.2f}%"
            )
    return salida


def main() -> None:
    parser = argparse.ArgumentParser(description="Validación independiente de churn y retención.")
    parser.add_argument("--ruta", default=RUTA_POR_DEFECTO, help="Ruta del csv o xlsx de ventas.")
    agregar_argumentos_datos(parser)
    parser.add_argument("--fecha-ref", default=None,
                        help="Fecha de referencia AAAA-MM-DD (por defecto: última venta).")
    parser.add_argument("--umbral", type=int, default=90, help="Días sin comprar para considerar churn.")
    parser.add_argument("--modo", choices=("global", "correcto"), default="global",
                        help="'global' replica la medida original; 'correcto' calcula 'a la fecha'.")
    parser.add_argument("--por-categoria", action="store_true",
                        help="Muestra la tabla por categoría (como el panel del reporte).")
    parser.add_argument("--sensibilidad", default=None,
                        help="Lista de umbrales separados por coma, ej. 30,60,90,180.")
    args = parser.parse_args()

    ventas = cargar_ventas(args.ruta, iva=args.iva, corregir_agencias=args.corregir_agencias)
    fecha_ref = pd.Timestamp(args.fecha_ref) if args.fecha_ref else fecha_ref_por_defecto(ventas)
    fecha_py = restar_meses(fecha_ref, 12)

    print(f"Fecha de referencia : {fecha_ref.date()}")
    print(f"Fecha ref. año ant. : {fecha_py.date()}")
    print(f"Umbral de churn     : {args.umbral} días")
    print(f"Modo                : {args.modo}")
    print("-" * 60)

    # --- Total general (fila 'Total' de la tabla del reporte) -----------
    actual = resumen_churn(ventas, fecha_ref, args.umbral, args.modo)
    previo = resumen_churn(ventas, fecha_py, args.umbral, args.modo)
    fila = actual.iloc[0]
    fila_py = previo.iloc[0]
    print("TOTAL GENERAL")
    print(f"  clientes_totales   : {int(fila['clientes_totales'])}")
    print(f"  clientes_con_churn : {int(fila['clientes_con_churn'])}")
    print(f"  churn_%            : {fila['churn_%'] * 100:.2f}%")
    print(f"  retencion_%        : {fila['retencion_%'] * 100:.2f}%")
    print(f"  churn_%_PY         : {fila_py['churn_%'] * 100:.2f}%   "
          f"(clientes_totales_PY = {int(fila_py['clientes_totales'])})")

    # --- Tabla por categoría --------------------------------------------
    if args.por_categoria:
        print("-" * 60)
        print("POR CATEGORÍA (ordenada por retención descendente)")
        tabla = tabla_abandono(ventas, fecha_ref, args.umbral, args.modo)
        with pd.option_context("display.max_rows", None, "display.width", 120):
            print(formatear_pct(tabla).to_string(index=False))

    # --- Sensibilidad al umbral -----------------------------------------
    if args.sensibilidad:
        print("-" * 60)
        print("SENSIBILIDAD AL UMBRAL (total general)")
        filas = []
        for texto in args.sensibilidad.split(","):
            umbral = int(texto)
            r = resumen_churn(ventas, fecha_ref, umbral, args.modo).iloc[0]
            filas.append(
                {
                    "umbral_dias": umbral,
                    "clientes_con_churn": int(r["clientes_con_churn"]),
                    "churn_%": f"{r['churn_%'] * 100:.2f}%",
                    "retencion_%": f"{r['retencion_%'] * 100:.2f}%",
                }
            )
        print(pd.DataFrame(filas).to_string(index=False))


if __name__ == "__main__":
    main()
