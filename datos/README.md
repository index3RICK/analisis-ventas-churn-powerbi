# Datos de origen

`ventas_tecnologia_barcelona.csv` — **961 líneas de venta** (320 facturas, 172 clientes), del 13-ene-2018 al 05-sep-2025. Son los datos **en bruto**, tal como vienen del curso: sin limpiar, para que puedas practicar la limpieza que se hace en este proyecto.


## Columnas

| Columna | Ejemplo | Cómo viene | Qué hay que hacer |
|---|---|---|---|
| `Agencia` | `Tech BCN Sur` | Texto | Unificar `Tech DCM Barcelona` con `Tech BCN Norte` |
| `Vendedor`, `Cliente`, `Ciudad`, `tipocliente` | `Nuria Pascual` | Texto | — |
| `DNI` | `DNI2896097998` | Texto | Datos inventados |
| `Factura` | `FAC000115` | Texto | Una factura tiene varias líneas |
| `Fecha` | `01-05-2018` | **Texto día-mes-año** (1 de mayo) | Convertir a fecha **sin** configuración regional `en-US` |
| `Precio` | `$124.43` | **Texto** con `$` y **punto decimal** | Convertir con configuración regional `en-US` (ver abajo) |
| `Cantidad` | `7` | Número entero | — |
| `Descuento` | `20%` | Porcentaje como texto | Convertir a porcentaje |
| `Iva` | `21%` | Porcentaje como texto | El archivo trae **21 %**; el modelo usa **15 %** |
| `Total` | `$843.14` | **Texto**, calculado con IVA 21 % | **No usar** si el modelo usa otro IVA |
| `codigocategoria`, `categorianombre` | `KVM`, `KVM Switches` | Texto | Relacionar por **código** |
| `marcanombre` | `DYNABOOK` | Texto | — |
| `codigoarticulo`, `descripcionarticulo` | `KVMDYNGHGK5BWI` | Texto | — |

## Cuatro trampas de este archivo (y cómo se resolvieron)

1. **Importes ×100.** `$124.43` usa punto decimal. Si Power BI lo lee con la configuración regional de un equipo en español de España, el punto es separador de miles y el precio pasa a 12,443. Solución: convertir `Precio` y `Total` con configuración regional `en-US` ([`codigo/powerquery/Analisis_Ventas.m`](../codigo/powerquery/Analisis_Ventas.m)).
2. **Fechas.** `01-05-2018` es día-mes-año. **No** apliques `en-US` a `Fecha`: se leería como 5 de enero.
3. **IVA.** El archivo trae 21 % (España). Este proyecto lo cambia a **15 %** (Ecuador). Con 21 %, la suma de ventas es 2,191,513.09; con 15 %, **2,082,843.02**.
4. **Una agencia con dos nombres.** `Tech DCM Barcelona` (221 filas) es la agencia Norte; hay que unificarla.

También hay un guion no estándar (U+2011) en 10 filas de `Access Points Wi‑Fi`: por eso las categorías se relacionan por código y no por nombre.

## Cifras de control

| | Con IVA del archivo (21 %) | Con IVA del modelo (15 %) |
|---|---|---|
| Ventas netas | 1,811,167.84 | 1,811,167.84 |
| IVA | 380,345.25 | 271,675.18 |
| **Ventas totales** | **2,191,513.09** | **2,082,843.02** |

Compruébalo con los scripts:

```bash
python codigo/python/validar_calidad_datos.py                                   # IVA del archivo
python codigo/python/validar_calidad_datos.py --iva 0.15 --corregir-agencias    # IVA del modelo
```
