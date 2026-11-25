"""
churn.py
========
Cálculo independiente de churn (abandono) y retención, para reconciliar con
las medidas DAX del reporte de Power BI.

Definición de negocio usada (la misma del reporte):
    * "Última compra" de un cliente = fecha máxima de sus compras.
    * Recencia (días) = fecha_ref - última compra.
    * Un cliente está en CHURN si recencia >= umbral (por defecto 90 días).
    * churn_%     = clientes_con_churn / clientes_totales
    * retencion_% = 1 - churn_%

Dos modos de calcular la "última compra" (parámetro `modo`):

    modo="global"     Replica la medida DAX original. La medida
                     [ultima_compra_cliente] usa ALL(DIM_Calendario), o sea
                     ignora el filtro de fecha: toma la última compra de TODO
                     el histórico. Con eso, para el año anterior (PY) solo se
                     cuentan clientes cuya última compra de toda la vida es
                     anterior a la fecha PY -> el churn PY sale inflado.

    modo="correcto"  Calcula la última compra "a la fecha": solo mira compras
                     hasta la fecha de referencia. Es lo que realmente
                     sabías el día del corte. Úsalo para validar la versión
                     mejorada (v2) del DAX.

Para el periodo actual, si la fecha de referencia es >= la última venta de los
datos, ambos modos dan el mismo resultado.
"""

from __future__ import annotations

import pandas as pd

MODOS_VALIDOS = ("global", "correcto")


def fecha_ref_por_defecto(ventas: pd.DataFrame) -> pd.Timestamp:
    """Última fecha con ventas. Es lo que hace la nueva medida Fecha_Ref."""
    return ventas["Fecha"].max()


def restar_meses(fecha: pd.Timestamp, meses: int) -> pd.Timestamp:
    """Equivalente a EDATE(fecha, -meses) de DAX/Excel."""
    return fecha - pd.DateOffset(months=meses)


def ultima_compra(
    ventas: pd.DataFrame,
    fecha_ref: pd.Timestamp,
    modo: str = "global",
    por_categoria: bool = False,
) -> pd.DataFrame:
    """
    Devuelve una fila por cliente (o por categoría+cliente) con su última compra.

    por_categoria=True replica el filtro de categoría que ve el DAX cuando la
    tabla del reporte tiene la categoría en las filas.
    """
    if modo not in MODOS_VALIDOS:
        raise ValueError(f"modo debe ser uno de {MODOS_VALIDOS}, recibí '{modo}'")

    base = ventas
    if modo == "correcto":
        # Solo compras hasta la fecha de corte.
        base = ventas[ventas["Fecha"] <= fecha_ref]
    # modo == "global": se usa todo el histórico (ALL(DIM_Calendario)).

    claves = ["codigocategoria", "Cliente"] if por_categoria else ["Cliente"]
    resultado = base.groupby(claves)["Fecha"].max().rename("ultima_compra").reset_index()

    # Igual que el DAX: se excluyen clientes cuya última compra es posterior
    # a la fecha de referencia (compras "en el futuro" del corte).
    return resultado[resultado["ultima_compra"] <= fecha_ref]


def resumen_churn(
    ventas: pd.DataFrame,
    fecha_ref: pd.Timestamp,
    umbral: int = 90,
    modo: str = "global",
    por_categoria: bool = False,
) -> pd.DataFrame:
    """
    Calcula clientes_totales, clientes_con_churn, churn_% y retencion_%.

    Si por_categoria=False devuelve una sola fila (total general).
    Si por_categoria=True devuelve una fila por categoría (código + nombre).
    """
    ultima = ultima_compra(ventas, fecha_ref, modo, por_categoria).copy()
    ultima["recencia_dias"] = (fecha_ref - ultima["ultima_compra"]).dt.days
    ultima["churn"] = (ultima["recencia_dias"] >= umbral).astype(int)

    if por_categoria:
        grupos = ultima.groupby("codigocategoria")
        resumen = grupos["churn"].agg(
            clientes_totales="size", clientes_con_churn="sum"
        ).reset_index()
        nombres = (
            ventas.drop_duplicates("codigocategoria")
            .set_index("codigocategoria")["categorianombre"]
        )
        resumen.insert(1, "categoria", resumen["codigocategoria"].map(nombres))
    else:
        resumen = pd.DataFrame(
            {
                "clientes_totales": [len(ultima)],
                "clientes_con_churn": [int(ultima["churn"].sum())],
            }
        )

    # DIVIDE de DAX devuelve vacío si el denominador es 0; aquí usamos NaN.
    resumen["churn_%"] = resumen["clientes_con_churn"] / resumen["clientes_totales"].where(
        resumen["clientes_totales"] > 0
    )
    resumen["retencion_%"] = 1 - resumen["churn_%"]
    return resumen


def tabla_abandono(
    ventas: pd.DataFrame,
    fecha_ref: pd.Timestamp,
    umbral: int = 90,
    modo: str = "global",
) -> pd.DataFrame:
    """
    Reproduce la tabla del panel 'Abandono de Clientes':
        categoria | retencion_% | churn_% | churn_%_PY
    ordenada por retención descendente (como en el reporte).
    """
    actual = resumen_churn(ventas, fecha_ref, umbral, modo, por_categoria=True)

    fecha_py = restar_meses(fecha_ref, 12)
    anterior = resumen_churn(ventas, fecha_py, umbral, modo, por_categoria=True)
    anterior = anterior[["codigocategoria", "churn_%"]].rename(columns={"churn_%": "churn_%_PY"})

    tabla = actual.merge(anterior, on="codigocategoria", how="left")
    tabla = tabla.sort_values(
        ["retencion_%", "categoria"], ascending=[False, True]
    ).reset_index(drop=True)
    return tabla[["categoria", "retencion_%", "churn_%", "churn_%_PY"]]
