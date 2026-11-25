# 2. Modelo de datos

## Esquema en estrella

```
                DIM_Calendario
                      │ 1
                      │
DIM_Agencias ──1──*  Analisis_Ventas  *──1── DIM_Clientes
                      │ *        │ *
                      │          └──── (Vendedor)
                      │ *
                 DIM_CatMarca
                   │ *      │ *
                   1        1
            DIM_Categoria  DIM_Marca
```


## Tabla de hechos

**`Analisis_Ventas`** — una fila por línea de factura (961 filas, 320 facturas).

| Columna | Tipo | Ejemplo | Nota |
|---|---|---|---|
| Agencia, Vendedor | Texto | Tech BCN Sur, Nuria Pascual | Ver nota de agencias abajo |
| Cliente, Ciudad, tipocliente, DNI | Texto | Sofía Pérez, Barcelona, Ecommerce | Un DNI por cliente |
| Factura | Texto | FAC000115 | Una fecha y un cliente por factura |
| Fecha | Fecha | 01-05-2018 | Viene como texto `dd-mm-aaaa`; se convierte en Power Query |
| Precio | Decimal | $124.43 | Viene como texto con `$` |
| Cantidad | Entero | 7 | 1 a 12 |
| Descuento | Porcentaje | 20% | 0 % a 20 %; viene como texto |
| Iva | Porcentaje | 21% | Siempre 21 % |
| Total | Decimal | $843.14 | Precio × Cantidad × (1 − Desc.) × (1 + IVA); se usa solo para validar |
| codigocategoria, categorianombre | Texto | KVM, KVM Switches | |
| marcanombre | Texto | DYNABOOK | |
| codigoarticulo, descripcionarticulo | Texto | KVMDYNGHGK5BWI | |

## Dimensiones

| Tabla | Filas | Clave | Cómo se crea |
|---|---|---|---|
| `DIM_Calendario` | 1 por día | `Fecha` | Tabla calculada ([`codigo/dax/tablas_calculadas/DIM_Calendario.dax`](../codigo/dax/tablas_calculadas/DIM_Calendario.dax)) |
| `DIM_Agencias` | 3 | `codAgencia` (BCN001–BCN003) | Tabla manual |
| `DIM_Categoria` | 50 | `codigo` | Tabla manual (código → nombre) |
| `DIM_Marca` | 26 | `codmarca` | Tabla manual |
| `DIM_CatMarca` | combinaciones únicas | `CatMarcaKey` | Tabla calculada ([`codigo/dax/tablas_calculadas/DIM_CatMarca.dax`](../codigo/dax/tablas_calculadas/DIM_CatMarca.dax)) |
| `DIM_Clientes` | 172 | `Cliente` | Valores únicos de las ventas |
| `DIM_Vendedor` | 10 | `Nombre` | Tabla manual |
| `Churn_Umbral` | 12 | — | Tabla de parámetros, **desconectada** |
| `Tasa_conversion`, `Margen_%` | — | — | Parámetros del panel de reactivación, **desconectados** |
| `Cliente_Segmento` | 5 | `Segmento` | Lista de segmentos para el segmentador, **desconectada** |

## Agencias y vendedores (resuelto)

La revisión automática (`codigo/python/validar_calidad_datos.py`) detectó dos cosas:

1. **Cuatro nombres de agencia en las ventas, tres en la dimensión.** `Tech DCM Barcelona` (221 filas, 23 %) era la agencia Norte con otro nombre. **Resuelto** en Power Query (→ `Tech BCN Norte`, ver [`Analisis_Ventas.m`](../codigo/powerquery/Analisis_Ventas.m)); ahora hay 3 agencias.
2. **Los 10 vendedores venden en las agencias.** Por eso una tabla `DIM_Vendedor` con una columna `Agencia` (cada vendedor en una sola) no refleja los datos. La agencia se relaciona **directamente desde la tabla de ventas**, no a través del vendedor.

## Buenas prácticas aplicadas

- **Esquema en estrella:** filtros de dimensiones hacia hechos, relaciones 1 a muchos.
- **Relacionar por código, no por nombre.** Ejemplo real: 10 filas usan `Access Points Wi‑Fi` con un guion especial (U+2011) distinto del guion normal; relacionando por nombre no coincidirían.
- **Tabla de fechas propia**, marcada como tal, en vez de las fechas automáticas de Power BI.
- **Medidas en tablas dedicadas** (`Medidas_churn`, `Medidas_Rate`...), no mezcladas con las columnas de datos.
- **Tabla de parámetros desconectada** para el umbral de churn.
