"""
Pruebas automáticas de la lógica de churn y de la limpieza de datos.

Ejecutar desde la raíz del repositorio:
    pip install -r requirements.txt pytest
    pytest -v

Usan datos inventados y pequeños (no dependen del xlsx), así que son rápidas
y cada caso se puede verificar a mano.
"""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "python"))

from cargar_datos import limpiar_dinero, limpiar_porcentaje, normalizar_texto  # noqa: E402
from churn import resumen_churn, restar_meses, ultima_compra  # noqa: E402


def hacer_ventas(filas):
    """Crea un DataFrame mínimo: (cliente, fecha, código de categoría)."""
    df = pd.DataFrame(filas, columns=["Cliente", "Fecha", "codigocategoria"])
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["categorianombre"] = df["codigocategoria"]
    return df


# ---------------------------------------------------------------- limpieza
def test_limpiar_dinero():
    assert limpiar_dinero(pd.Series(["$1,075.53", "$6.46"])).tolist() == [1075.53, 6.46]


def test_limpiar_porcentaje():
    assert limpiar_porcentaje(pd.Series(["20%", "0%"])).tolist() == [0.20, 0.0]


def test_normalizar_guion_no_separable():
    assert normalizar_texto(pd.Series(["Access Points Wi‑Fi "])).iloc[0] == "Access Points Wi-Fi"


# ------------------------------------------------------------------ fechas
def test_restar_meses_equivale_a_edate():
    assert restar_meses(pd.Timestamp("2025-09-05"), 12) == pd.Timestamp("2024-09-05")
    # 29-feb en año bisiesto -> 28-feb del año anterior (igual que EDATE)
    assert restar_meses(pd.Timestamp("2024-02-29"), 12) == pd.Timestamp("2023-02-28")


# ------------------------------------------------------------------ umbral
def test_umbral_es_mayor_o_igual():
    """Recencia == umbral cuenta como churn (>=), igual que en el DAX."""
    ventas = hacer_ventas(
        [
            ("A", "2025-06-07", "X"),  # 90 días antes del 2025-09-05 -> churn
            ("B", "2025-06-08", "X"),  # 89 días -> activo
        ]
    )
    r = resumen_churn(ventas, pd.Timestamp("2025-09-05"), umbral=90).iloc[0]
    assert r["clientes_totales"] == 2
    assert r["clientes_con_churn"] == 1


def test_retencion_es_complemento_de_churn():
    ventas = hacer_ventas([("A", "2025-01-01", "X"), ("B", "2025-09-01", "X")])
    r = resumen_churn(ventas, pd.Timestamp("2025-09-05"), umbral=90).iloc[0]
    assert r["churn_%"] == pytest.approx(0.5)
    assert r["retencion_%"] == pytest.approx(0.5)
    assert r["churn_%"] + r["retencion_%"] == pytest.approx(1.0)


# ------------------------------------------------------------ clientes
def test_clientes_con_compra_posterior_al_corte_se_excluyen_en_modo_global():
    """
    Modo 'global' (medida DAX original): [ultima_compra_cliente] ignora el filtro de
    fecha, así que un cliente que compró DESPUÉS del corte no se cuenta.
    """
    ventas = hacer_ventas([("A", "2024-01-01", "X"), ("A", "2025-06-01", "X")])
    corte = pd.Timestamp("2024-06-01")
    assert len(ultima_compra(ventas, corte, modo="global")) == 0


def test_modo_correcto_usa_solo_compras_hasta_el_corte():
    """Modo 'correcto': el mismo cliente SÍ cuenta, con su compra de 2024-01-01."""
    ventas = hacer_ventas([("A", "2024-01-01", "X"), ("A", "2025-06-01", "X")])
    corte = pd.Timestamp("2024-06-01")
    resultado = ultima_compra(ventas, corte, modo="correcto")
    assert len(resultado) == 1
    assert resultado["ultima_compra"].iloc[0] == pd.Timestamp("2024-01-01")


def test_modo_invalido_lanza_error():
    ventas = hacer_ventas([("A", "2024-01-01", "X")])
    with pytest.raises(ValueError):
        ultima_compra(ventas, pd.Timestamp("2024-06-01"), modo="otro")


# ------------------------------------------------------------ categorías
def test_churn_se_calcula_por_categoria():
    """Un cliente puede estar activo en una categoría y en churn en otra."""
    ventas = hacer_ventas(
        [
            ("A", "2025-09-01", "LAP"),  # compra reciente en laptops
            ("A", "2024-01-01", "MOU"),  # hace mucho en mouse
        ]
    )
    r = resumen_churn(ventas, pd.Timestamp("2025-09-05"), umbral=90, por_categoria=True)
    por_cat = r.set_index("codigocategoria")
    assert por_cat.loc["LAP", "clientes_con_churn"] == 0
    assert por_cat.loc["MOU", "clientes_con_churn"] == 1
    # ...pero a nivel cliente (sin categoría) está activo:
    assert resumen_churn(ventas, pd.Timestamp("2025-09-05"), umbral=90).iloc[0]["clientes_con_churn"] == 0
