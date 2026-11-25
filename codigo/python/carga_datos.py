"""
cargar_datos.py
================
Carga y limpieza del archivo de ventas (ventas_tecnologia_barcelona.xlsx).

¿Para qué sirve?
    Los datos originales traen los números como TEXTO ("$124.43", "20%") y las
    fechas como texto ("01-05-2018"). Power BI los convierte en Power Query;
    aquí hacemos lo mismo en pandas para poder VALIDAR que las medidas DAX
    dan los mismos resultados que un cálculo independiente.

Uso desde otro script:
    from cargar_datos import cargar_ventas
    ventas = cargar_ventas("datos/ventas_tecnologia_barcelona.csv", iva=0.15)

Columnas nuevas que agrega (equivalen a las medidas DAX de facturación,
pero calculadas fila por fila):
    importe_bruto   = Precio * Cantidad
    descuento_usd   = Precio * Cantidad * Descuento
    ventas_netas    = importe_bruto - descuento_usd
    iva_usd         = ventas_netas * Iva
    ventas_totales  = ventas_netas + iva_usd
"""

from __future__ import annotations

import pandas as pd

# Ruta por defecto: la que se usa en el README del proyecto.
RUTA_POR_DEFECTO = "datos/ventas_tecnologia_barcelona.csv"

# Formato de fecha del archivo original (día-mes-año).
FORMATO_FECHA = "%d-%m-%Y"

# El guion "no separable" (U+2011) aparece en "Access Points Wi‑Fi" y rompe
# las comparaciones de texto con el guion normal "-". Lo normalizamos.
GUION_NO_SEPARABLE = "‑"


def limpiar_dinero(serie: pd.Series) -> pd.Series:
    """Convierte textos como '$1,075.53' a número (1075.53)."""
    return (
        serie.astype(str)
        .str.replace(r"[$,\s]", "", regex=True)
        .astype(float)
    )


def limpiar_porcentaje(serie: pd.Series) -> pd.Series:
    """Convierte textos como '20%' a fracción (0.20)."""
    return serie.astype(str).str.replace("%", "", regex=False).astype(float) / 100


def normalizar_texto(serie: pd.Series) -> pd.Series:
    """Quita espacios sobrantes y reemplaza el guion no separable por '-'."""
    return (
        serie.astype(str)
        .str.replace(GUION_NO_SEPARABLE, "-", regex=False)
        .str.strip()
    )


AGENCIA_A_CORREGIR = "Tech DCM Barcelona"
AGENCIA_CORRECTA = "Tech BCN Norte"


def agregar_argumentos_datos(parser) -> None:
    """Agrega a un argparse las opciones comunes de limpieza (--iva, --corregir-agencias)."""
    parser.add_argument(
        "--iva", type=float, default=None,
        help="Tasa de IVA del modelo (ej. 0.15). Si no se indica, se usa la del archivo (0.21).",
    )
    parser.add_argument(
        "--corregir-agencias", action="store_true",
        help=f"Reemplaza '{AGENCIA_A_CORREGIR}' por '{AGENCIA_CORRECTA}' (igual que en Power Query).",
    )


def cargar_ventas(
    ruta: str = RUTA_POR_DEFECTO,
    hoja: str = "ventas",
    iva: float | None = None,
    corregir_agencias: bool = False,
) -> pd.DataFrame:
    """
    Lee las ventas (.csv o .xlsx) y devuelve un DataFrame limpio.

    Parámetros
    ----------
    ruta : ruta del .csv (recomendado) o del .xlsx original.
    hoja : nombre de la hoja si es .xlsx (en el archivo original se llama 'ventas').
    iva : si se indica (ej. 0.15), sustituye la tasa de IVA de TODAS las filas,
          igual que el paso de Power Query del modelo. El archivo original trae
          21 % (España); el modelo de este proyecto usa 15 % (Ecuador).
    corregir_agencias : si es True, 'Tech DCM Barcelona' pasa a 'Tech BCN Norte'.

    Notas
    -----
    * Las fechas inválidas quedan como NaT (no se descartan aquí; eso lo
      reporta `validar_calidad_datos.py`).
    * No modifica el archivo original: trabaja sobre una copia en memoria.
    * Se agrega la columna `ventas_totales_origen`: el total calculado con el
      IVA del archivo, que es el que debe cuadrar con la columna `Total`.
    """
    if str(ruta).lower().endswith(".csv"):
        ventas = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
        ventas["Cantidad"] = pd.to_numeric(ventas["Cantidad"])
    else:
        ventas = pd.read_excel(ruta, sheet_name=hoja)

    # --- Fechas: texto -> datetime ---------------------------------------
    ventas["Fecha"] = pd.to_datetime(
        ventas["Fecha"], format=FORMATO_FECHA, errors="coerce"
    )

    # --- Números guardados como texto -> float -------------------------
    ventas["Precio"] = limpiar_dinero(ventas["Precio"])
    ventas["Total"] = limpiar_dinero(ventas["Total"])
    ventas["Descuento"] = limpiar_porcentaje(ventas["Descuento"])
    ventas["Iva"] = limpiar_porcentaje(ventas["Iva"])

    iva_origen = ventas["Iva"].copy()
    if iva is not None:
        ventas["Iva"] = float(iva)

    # --- Texto: normalizar columnas que se usan para agrupar ------------
    for columna in ("categorianombre", "marcanombre", "Agencia", "Vendedor", "Cliente"):
        ventas[columna] = normalizar_texto(ventas[columna])

    # --- Equivalentes fila a fila de las medidas de facturación ---------
    ventas["importe_bruto"] = ventas["Precio"] * ventas["Cantidad"]
    ventas["descuento_usd"] = ventas["importe_bruto"] * ventas["Descuento"]
    ventas["ventas_netas"] = ventas["importe_bruto"] - ventas["descuento_usd"]
    ventas["iva_usd"] = ventas["ventas_netas"] * ventas["Iva"]
    ventas["ventas_totales"] = ventas["ventas_netas"] + ventas["iva_usd"]
    ventas["ventas_totales_origen"] = ventas["ventas_netas"] * (1 + iva_origen)

    if corregir_agencias:
        ventas["Agencia"] = ventas["Agencia"].replace(AGENCIA_A_CORREGIR, AGENCIA_CORRECTA)

    return ventas
