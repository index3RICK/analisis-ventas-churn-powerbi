"""
validar_calidad_datos.py
========================
Revisa la calidad del archivo de ventas ANTES de construir medidas en Power BI.

Regla de oro del análisis de datos: nunca confíes en un número hasta haber
revisado de dónde viene. Este script automatiza las revisiones que conviene
hacer siempre al recibir una base nueva.

Niveles del reporte:
    OK           la revisión pasó
    ADVERTENCIA  no rompe cálculos, pero conviene entenderlo/corregirlo
    ERROR        puede producir números incorrectos en el reporte

Uso (desde la raíz del repositorio):
    python python/validar_calidad_datos.py
    python python/validar_calidad_datos.py --ruta datos/ventas_tecnologia_barcelona.csv --iva 0.15 --corregir-agencias
    python python/validar_calidad_datos.py --salida docs/reporte_calidad.md

Código de salida: 0 si no hay ERRORES, 1 si hay al menos uno (útil para
automatizar la validación en una canalización de datos).
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cargar_datos import FORMATO_FECHA, GUION_NO_SEPARABLE, RUTA_POR_DEFECTO, agregar_argumentos_datos, cargar_ventas  # noqa: E402

# Agencias que existen en tu dimensión DIM_Agencias. Si en las ventas aparece
# otra, esas filas quedarán SIN agencia en los visuales.
AGENCIAS_DIMENSION = ["Tech BCN Norte", "Tech BCN Centro", "Tech BCN Sur"]

PATRON_DNI = re.compile(r"^DNI\d{10}$")
TOLERANCIA_TOTAL = 0.02  # diferencia máxima aceptada en dólares entre Total y el cálculo


def revisar(ventas: pd.DataFrame, texto_fechas: pd.Series, agencias_dim: list[str]) -> list[tuple[str, str, str]]:
    """Ejecuta todas las revisiones y devuelve (nivel, nombre, detalle)."""
    resultados: list[tuple[str, str, str]] = []

    def agregar(nivel: str, nombre: str, detalle: str) -> None:
        resultados.append((nivel, nombre, detalle))

    # 1. Volumen básico ---------------------------------------------------
    agregar(
        "OK",
        "Volumen",
        f"{len(ventas)} filas, {ventas['Factura'].nunique()} facturas, "
        f"{ventas['Cliente'].nunique()} clientes, "
        f"rango de fechas {ventas['Fecha'].min().date()} a {ventas['Fecha'].max().date()}",
    )

    # 2. Valores vacíos -------------------------------------------------
    nulos = ventas.isna().sum()
    nulos = nulos[nulos > 0]
    if nulos.empty:
        agregar("OK", "Valores vacíos", "Ninguna columna tiene vacíos")
    else:
        agregar("ERROR", "Valores vacíos", "; ".join(f"{c}: {n}" for c, n in nulos.items()))

    # 3. Filas duplicadas exactas ------------------------------------------
    duplicadas = int(ventas.duplicated().sum())
    if duplicadas == 0:
        agregar("OK", "Filas duplicadas", "No hay filas idénticas")
    else:
        agregar("ERROR", "Filas duplicadas", f"{duplicadas} filas exactamente repetidas (inflan las ventas)")

    # 4. Fechas que no se pudieron convertir --------------------------------
    invalidas = int(ventas["Fecha"].isna().sum())
    if invalidas == 0:
        agregar("OK", "Formato de fecha", f"Todas las fechas cumplen el formato {FORMATO_FECHA}")
    else:
        ejemplos = texto_fechas[ventas["Fecha"].isna()].head(3).tolist()
        agregar("ERROR", "Formato de fecha", f"{invalidas} fechas inválidas, ej.: {ejemplos}")

    # 5. DNI: formato y relación 1 a 1 con el cliente -----------------------
    dni_mal = ventas.loc[~ventas["DNI"].astype(str).str.match(PATRON_DNI), ["Cliente", "DNI"]].drop_duplicates()
    if dni_mal.empty:
        agregar("OK", "Formato de DNI", "Todos cumplen DNI + 10 dígitos")
    else:
        agregar("ADVERTENCIA", "Formato de DNI", f"{len(dni_mal)} DNI fuera de patrón, ej.: {dni_mal.head(3).values.tolist()}")

    dni_por_cliente = ventas.groupby("Cliente")["DNI"].nunique()
    cliente_por_dni = ventas.groupby("DNI")["Cliente"].nunique()
    if (dni_por_cliente > 1).any() or (cliente_por_dni > 1).any():
        agregar(
            "ERROR",
            "Cliente <-> DNI",
            f"{int((dni_por_cliente > 1).sum())} clientes con varios DNI y "
            f"{int((cliente_por_dni > 1).sum())} DNI con varios clientes "
            "(la relación con DIM_Clientes dará resultados duplicados)",
        )
    else:
        agregar("OK", "Cliente <-> DNI", "Cada cliente tiene un solo DNI y viceversa")

    # 6. Cada factura debe tener una sola fecha y un solo cliente -----------
    por_factura = ventas.groupby("Factura").agg(fechas=("Fecha", "nunique"), clientes=("Cliente", "nunique"))
    malas = por_factura[(por_factura["fechas"] > 1) | (por_factura["clientes"] > 1)]
    if malas.empty:
        agregar("OK", "Consistencia de facturas", "Cada factura tiene una fecha y un cliente")
    else:
        agregar("ERROR", "Consistencia de facturas", f"{len(malas)} facturas con varias fechas o clientes")

    # 7. Total reportado vs total recalculado ----------------------------
    diferencia = (ventas["Total"] - ventas["ventas_totales_origen"]).abs()
    filas_mal = int((diferencia > TOLERANCIA_TOTAL).sum())
    if filas_mal == 0:
        agregar(
            "OK",
            "Total reportado vs calculado",
            f"Coincide fila por fila (suma = {ventas['Total'].sum():,.2f}). "
            "Es el total con el IVA del archivo (21 %). Si el modelo usa otro IVA, ejecuta con --iva para ver la cifra que debe cuadrar con [ventas_totales].",
        )
    else:
        agregar("ERROR", "Total reportado vs calculado", f"{filas_mal} filas con diferencia > {TOLERANCIA_TOTAL}")

    # 7b. Cifra de control del modelo (si se cambió el IVA con --iva) ------
    if (ventas["ventas_totales"] - ventas["ventas_totales_origen"]).abs().max() > TOLERANCIA_TOTAL:
        agregar(
            "OK",
            "Cifra de control del modelo",
            f"Con el IVA del modelo ({ventas['Iva'].iloc[0]:.0%}): ventas_netas = {ventas['ventas_netas'].sum():,.2f}, "
            f"iva_usd = {ventas['iva_usd'].sum():,.2f}, ventas_totales = {ventas['ventas_totales'].sum():,.2f}. "
            "Estas son las cifras que deben dar las medidas en Power BI sin filtros.",
        )

    # 8. Rangos lógicos --------------------------------------------------
    problemas = []
    if (ventas["Cantidad"] <= 0).any():
        problemas.append("Cantidad <= 0")
    if (ventas["Precio"] <= 0).any():
        problemas.append("Precio <= 0")
    if ((ventas["Descuento"] < 0) | (ventas["Descuento"] > 1)).any():
        problemas.append("Descuento fuera de 0%-100%")
    if problemas:
        agregar("ERROR", "Rangos lógicos", "; ".join(problemas))
    else:
        agregar(
            "OK",
            "Rangos lógicos",
            f"Cantidad {ventas['Cantidad'].min()}-{ventas['Cantidad'].max()}, "
            f"precio {ventas['Precio'].min():,.2f}-{ventas['Precio'].max():,.2f}, "
            f"descuento {ventas['Descuento'].min():.0%}-{ventas['Descuento'].max():.0%}",
        )

    # 9. Caracteres especiales en nombres --------------------------------
    if str(RUTA_ACTUAL[0]).lower().endswith(".csv"):
        crudo = pd.read_csv(RUTA_ACTUAL[0], dtype=str, usecols=["categorianombre"], encoding="utf-8-sig")
    else:
        crudo = pd.read_excel(RUTA_ACTUAL[0], sheet_name="ventas", usecols=["categorianombre"])
    con_guion = int(crudo["categorianombre"].astype(str).str.contains(GUION_NO_SEPARABLE).sum())
    if con_guion:
        agregar(
            "ADVERTENCIA",
            "Guion no estándar en categorías",
            f"{con_guion} filas usan el guion U+2011 (ej. 'Access Points Wi{GUION_NO_SEPARABLE}Fi'). "
            "Si relacionas por NOMBRE (no por código) no coincidirá con 'Wi-Fi'. Relaciona por código.",
        )
    else:
        agregar("OK", "Caracteres especiales", "Sin guiones no estándar")

    # 10. Agencias de las ventas vs dimensión -------------------------------
    en_ventas = sorted(ventas["Agencia"].unique())
    sin_dim = [a for a in en_ventas if a not in agencias_dim]
    if sin_dim:
        filas = int(ventas["Agencia"].isin(sin_dim).sum())
        agregar(
            "ERROR",
            "Agencias sin dimensión",
            f"{sin_dim} aparece(n) en ventas pero no en DIM_Agencias: {filas} filas "
            f"({filas / len(ventas):.0%}) quedarán sin agencia en los visuales. "
            "En el proyecto se corrige en Power Query (Tech DCM Barcelona -> Tech BCN Norte); "
            "aquí puedes simularlo con --corregir-agencias.",
        )
    else:
        agregar("OK", "Agencias", "Todas las agencias de ventas existen en la dimensión")

    # 11. Vendedor asignado a una sola agencia -------------------------------
    agencias_por_vendedor = ventas.groupby("Vendedor")["Agencia"].nunique()
    multi = agencias_por_vendedor[agencias_por_vendedor > 1]
    if multi.empty:
        agregar("OK", "Vendedor <-> Agencia", "Cada vendedor pertenece a una sola agencia")
    else:
        agregar(
            "ADVERTENCIA",
            "Vendedor <-> Agencia",
            f"{len(multi)} de {len(agencias_por_vendedor)} vendedores venden en más de una agencia "
            f"(máx. {int(multi.max())}). DIM_Vendedor no puede ser 'vendedor -> agencia'; "
            "relaciona la agencia directo desde la tabla de ventas.",
        )

    return resultados


# Ruta del archivo en uso (se llena en main; se usa en la revisión 9).
RUTA_ACTUAL: list[str] = [RUTA_POR_DEFECTO]


def main() -> int:
    parser = argparse.ArgumentParser(description="Revisión de calidad de datos del archivo de ventas.")
    parser.add_argument("--ruta", default=RUTA_POR_DEFECTO, help="Ruta del csv o xlsx de ventas.")
    agregar_argumentos_datos(parser)
    parser.add_argument("--agencias", default=",".join(AGENCIAS_DIMENSION),
                        help="Agencias que existen en DIM_Agencias, separadas por coma.")
    parser.add_argument("--salida", default=None, help="Si se indica, guarda el reporte en este .md.")
    args = parser.parse_args()

    RUTA_ACTUAL[0] = args.ruta
    if str(args.ruta).lower().endswith(".csv"):
        texto_fechas = pd.read_csv(args.ruta, dtype=str, usecols=["Fecha"], encoding="utf-8-sig")["Fecha"]
    else:
        texto_fechas = pd.read_excel(args.ruta, sheet_name="ventas", usecols=["Fecha"])["Fecha"].astype(str)
    ventas = cargar_ventas(args.ruta, iva=args.iva, corregir_agencias=args.corregir_agencias)
    agencias_dim = [a.strip() for a in args.agencias.split(",")]

    resultados = revisar(ventas, texto_fechas, agencias_dim)

    iconos = {"OK": "[OK]         ", "ADVERTENCIA": "[ADVERTENCIA]", "ERROR": "[ERROR]      "}
    for nivel, nombre, detalle in resultados:
        print(f"{iconos[nivel]} {nombre}: {detalle}")

    errores = sum(1 for n, _, _ in resultados if n == "ERROR")
    advertencias = sum(1 for n, _, _ in resultados if n == "ADVERTENCIA")
    print("-" * 70)
    print(f"Resumen: {errores} error(es), {advertencias} advertencia(s), "
          f"{len(resultados) - errores - advertencias} revisión(es) sin problema")

    if args.salida:
        lineas = ["# Reporte de calidad de datos", "",
                  f"Archivo: `{args.ruta}`", "",
                  "| Nivel | Revisión | Detalle |", "|---|---|---|"]
        lineas += [f"| {n} | {nom} | {det} |" for n, nom, det in resultados]
        lineas += ["", f"**Resumen:** {errores} error(es), {advertencias} advertencia(s)."]
        with open(args.salida, "w", encoding="utf-8") as archivo:
            archivo.write("\n".join(lineas) + "\n")
        print(f"Reporte guardado en {args.salida}")

    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
