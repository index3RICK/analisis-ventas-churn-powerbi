
# Scripts de Python

Scripts para **validar** las cifras del reporte con un cálculo independiente. No reemplazan a Power BI: sirven para comprobar que sus medidas están bien.

## Instalación

```bash
pip install -r ../requirements.txt     # pandas y openpyxl
```

Ejecuta los scripts **desde la raíz del repositorio** (por la ruta por defecto de los datos), aunque funcionan desde cualquier carpeta si pasas `--ruta`.

## Scripts

| Script | Qué hace |
|---|---|
| [`cargar_datos.py`](cargar_datos.py) | Lee y limpia el xlsx: fechas, dinero y porcentajes a números; normaliza guiones; calcula la cadena de facturación fila por fila |
| [`churn.py`](churn.py) | Lógica de churn y retención (biblioteca reutilizable, con dos modos: `global` y `correcto`) |
| [`validar_calidad_datos.py`](validar_calidad_datos.py) | 12 revisiones de calidad (nulos, duplicados, DNI, totales, agencias...) con nivel OK/ADVERTENCIA/ERROR |
| [`validar_churn.py`](validar_churn.py) | Total y tabla por categoría, comparable con el panel de Power BI; análisis de sensibilidad al umbral |
| [`ejecutar_sql.py`](ejecutar_sql.py) | Ejecuta `codigo/sql/churn_por_categoria.sql` en SQLite en memoria y lo compara con pandas |

## Ejemplos

```bash
python codigo/python/validar_calidad_datos.py --iva 0.15 --corregir-agencias
python codigo/python/validar_churn.py --por-categoria --umbral 120
python codigo/python/validar_churn.py --fecha-ref 2025-10-02 --por-categoria     # otra fecha de corte
python codigo/python/validar_churn.py --sensibilidad 30,60,90,120,180
python codigo/python/validar_churn.py --umbral 120 --modo correcto       # valida las medidas PY finales (92.50 %)
python codigo/python/ejecutar_sql.py --umbral 120 --comparar
```

## Los dos modos de churn

| Modo | Qué replica |
|---|---|
| `global` (por defecto) | La medida DAX original: la última compra de cada cliente es la de **todo** el histórico (`ALL(DIM_Calendario)`) |
| `correcto` | La última compra "a la fecha de corte": solo se miran compras hasta esa fecha. Equivale al SQL y a las medidas `_PY_v2` |

Para la fecha actual (cuando el corte es la última venta) ambos modos coinciden. Se diferencian en el año anterior.

## Cómo interpretar los resultados

- Si el **total de churn actual** coincide con Power BI (misma fecha y umbral): las medidas están bien.
- Si no coincide, el primer paso es revisar la **fecha de referencia** y el **umbral**; son las dos causas más comunes.
- El `Churn_%_PY` solo coincide en algunas filas y no en el total (ver `docs/05_lecciones_aprendidas.md`, lección 4).

## Pruebas

```bash
pip install pytest
pytest -v        # desde la raíz del repositorio
```

Código de salida de `validar_calidad_datos.py`: `0` sin errores, `1` con al menos un error (útil para automatizar).
