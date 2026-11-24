
# Código DAX — una medida por archivo

Cada archivo trae, arriba, un bloque de comentarios en español con **qué hace**, **en qué paneles se usa** y las **notas** importantes (errores corregidos, supuestos). Debajo está el código tal como quedó en el reporte final.

Convención: la carpeta es la **tabla de medidas** donde vive la medida en Power BI; el archivo se llama como la medida en minúsculas (`%` se escribe `pct`, los paréntesis y espacios se cambian por `_`).

Paneles: **1** Cuadro de mando · **2** Detalle de ventas global · **3** Abandono de clientes · **4** Reactivación de clientes.

## Tablas calculadas y parámetros

| Archivo | Qué es | Paneles |
|---|---|---|
| [`tablas_calculadas/DIM_Calendario.dax`](tablas_calculadas/DIM_Calendario.dax) | Tabla de fechas continua | todos |
| [`tablas_calculadas/DIM_CatMarca.dax`](tablas_calculadas/DIM_CatMarca.dax) | Tabla puente categoría–marca | 1 |
| [`parametros/Churn_Umbral.dax`](parametros/Churn_Umbral.dax) | Control del umbral de abandono (15–180 días) | 3, 4 |
| [`parametros/Tasa_conversion.dax`](parametros/Tasa_conversion.dax) | Supuesto de conversión | 4 |
| [`parametros/Margen_pct.dax`](parametros/Margen_pct.dax) | Supuesto de margen | 4 |
| [`parametros/Cliente_Segmento.dax`](parametros/Cliente_Segmento.dax) | Lista de segmentos del segmentador | 4 |

## Medidas_base_facturacion

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `importe_bruto` | Lo que se habría cobrado sin descuentos: Precio x Cantidad, calculado fila por fila y luego sumado. | 1, 2 | [importe_bruto.dax](Medidas_base_facturacion/importe_bruto.dax) |
| `descuento_usd` | Dinero descontado: Precio x Cantidad x Descuento, fila por fila. | 1, 2 | [descuento_usd.dax](Medidas_base_facturacion/descuento_usd.dax) |
| `ventas_netas` | Venta después de descuentos y antes de IVA. | 1, 2 | [ventas_netas.dax](Medidas_base_facturacion/ventas_netas.dax) |
| `iva_usd` | IVA cobrado: se aplica sobre el valor ya descontado de cada fila. | 1, 2 | [iva_usd.dax](Medidas_base_facturacion/iva_usd.dax) |
| `ventas_totales` | Venta total con IVA = ventas_netas + iva_usd. Es la medida principal del proyecto. | 1, 2, 3, 4 | [ventas_totales.dax](Medidas_base_facturacion/ventas_totales.dax) |
| `unidades_vendidas` | Número de piezas vendidas. | 1 | [unidades_vendidas.dax](Medidas_base_facturacion/unidades_vendidas.dax) |
| `precio_promedio` | Precio medio por unidad (bruto): importe_bruto / unidades. | 1 | [precio_promedio.dax](Medidas_base_facturacion/precio_promedio.dax) |
| `ticket_promedio` | Venta neta promedio por factura (una factura tiene varias filas). | 1 | [ticket_promedio.dax](Medidas_base_facturacion/ticket_promedio.dax) |

## Medidas_Inteligencia_Tiempo

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `ventas_mes_anterior` | Ventas del mes anterior (desplaza el contexto un mes atrás con DATEADD). | 2 | [ventas_mes_anterior.dax](Medidas_Inteligencia_Tiempo/ventas_mes_anterior.dax) |
| `ventas_totales_ly` | Ventas del mismo periodo del año anterior (SAMEPERIODLASTYEAR). Alimenta "Referencia LY". | 2, 3 | [ventas_totales_ly.dax](Medidas_Inteligencia_Tiempo/ventas_totales_ly.dax) |
| `crecimiento_mom` | Variación porcentual contra el mes anterior. | 2 | [crecimiento_mom.dax](Medidas_Inteligencia_Tiempo/crecimiento_mom.dax) |
| `crecimiento_yoy` | Variación porcentual contra el mismo periodo del año anterior. Es el "(%) Creci / Decre". | 2 | [crecimiento_yoy.dax](Medidas_Inteligencia_Tiempo/crecimiento_yoy.dax) |

## Medidas_participacion_ranking

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `numero_clientes_unicos` | Clientes distintos (DISTINCTCOUNT). | 1, 2 | [numero_clientes_unicos.dax](Medidas_participacion_ranking/numero_clientes_unicos.dax) |
| `%_participacion_cliente` | % de clientes sobre el total absoluto (ALL: ignora segmentadores). | 2 | [pct_participacion_cliente.dax](Medidas_participacion_ranking/pct_participacion_cliente.dax) |
| `%_participacion_ventas` | % de ventas sobre lo que el usuario está viendo (ALLSELECTED). | 2 | [pct_participacion_ventas.dax](Medidas_participacion_ranking/pct_participacion_ventas.dax) |
| `ranking_venta_clientes` | Posición de cada cliente por ventas (1 = el que más compra). | 2 | [ranking_venta_clientes.dax](Medidas_participacion_ranking/ranking_venta_clientes.dax) |
| `ranking_ventas_vendedor` | Posición de cada vendedor por ventas. | 2 | [ranking_ventas_vendedor.dax](Medidas_participacion_ranking/ranking_ventas_vendedor.dax) |
| `acum_ventas_cliente` | Venta acumulada de los clientes hasta la posición actual (base del Pareto). | 2 | [acum_ventas_cliente.dax](Medidas_participacion_ranking/acum_ventas_cliente.dax) |
| `acum_ventas_vendedor` | Venta acumulada de los vendedores hasta la posición actual. | 2 | [acum_ventas_vendedor.dax](Medidas_participacion_ranking/acum_ventas_vendedor.dax) |
| `%_acum_pareto_clientes` | % acumulado de la venta por cliente (curva 80/20). | 2 | [pct_acum_pareto_clientes.dax](Medidas_participacion_ranking/pct_acum_pareto_clientes.dax) |
| `%_acum_pareto_vendedor` | % acumulado de la venta por vendedor. Es la barra de "Fuerza de ventas (Ejecutivo)". | 2 | [pct_acum_pareto_vendedor.dax](Medidas_participacion_ranking/pct_acum_pareto_vendedor.dax) |

## Medidas_churn

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `Fecha_Ref` | Fecha de corte del análisis. Nunca pasa de la última venta real. | 3, 4 | [fecha_ref.dax](Medidas_churn/fecha_ref.dax) |
| `churn_umbral_dias_value` | Umbral elegido en el control "Umbral" (días sin comprar = abandono). | 3, 4 | [churn_umbral_dias_value.dax](Medidas_churn/churn_umbral_dias_value.dax) |
| `ultima_compra_cliente` | Fecha de la última compra de cada cliente, ignorando el filtro de fecha. | 3, 4 | [ultima_compra_cliente.dax](Medidas_churn/ultima_compra_cliente.dax) |
| `Recency_(dias)` | R de RFM: días desde la última compra hasta Fecha_Ref. | 3, 4 | [recency_dias.dax](Medidas_churn/recency_dias.dax) |
| `churn_flag` | 1 si el cliente está en churn (recencia >= umbral), 0 si está activo. Se evalúa cliente por cliente. | 3, 4 | [churn_flag.dax](Medidas_churn/churn_flag.dax) |
| `clientes_totales` | Clientes que han comprado alguna vez hasta la fecha de referencia. | 3, 4 | [clientes_totales.dax](Medidas_churn/clientes_totales.dax) |
| `clientes_con_churn` | Suma de los churn_flag = clientes en abandono. | 3, 4 | [clientes_con_churn.dax](Medidas_churn/clientes_con_churn.dax) |
| `clientes_activos` | clientes_totales - clientes_con_churn. | 3, 4 | [clientes_activos.dax](Medidas_churn/clientes_activos.dax) |
| `churn_%` | Porcentaje de abandono = clientes_con_churn / clientes_totales. | 3 | [churn_pct.dax](Medidas_churn/churn_pct.dax) |
| `Retencion_%` | 1 - churn_%. Devuelve BLANK si no hay clientes. | 3 | [retencion_pct.dax](Medidas_churn/retencion_pct.dax) |
| `Frecuency_Facturas` | F de RFM: facturas distintas hasta la fecha de referencia. | 3 | [frecuency_facturas.dax](Medidas_churn/frecuency_facturas.dax) |
| `Monetary_Ventas` | M de RFM: valor comprado hasta la fecha de referencia. | 3 | [monetary_ventas.dax](Medidas_churn/monetary_ventas.dax) |

## Medidas_Rate

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `Fecha_Ref_PY` | Fecha de corte del año anterior: la misma fecha, 12 meses atrás (EDATE). | 3 | [fecha_ref_py.dax](Medidas_Rate/fecha_ref_py.dax) |
| `Clientes_totales_PY` | Clientes que ya habían comprado al corte del año anterior. | 3 | [clientes_totales_py.dax](Medidas_Rate/clientes_totales_py.dax) |
| `Clientes_con_Churn_PY` | Clientes en churn al corte del año anterior. | 3 | [clientes_con_churn_py.dax](Medidas_Rate/clientes_con_churn_py.dax) |
| `Clientes_Activo_PY` | Clientes activos al corte del año anterior = totales PY - churn PY. | 3 | [clientes_activo_py.dax](Medidas_Rate/clientes_activo_py.dax) |
| `Churn_%_PY` | Tasa de churn del año anterior. Con el panel final (umbral 120): 91.94 %. | 3 | [churn_pct_py.dax](Medidas_Rate/churn_pct_py.dax) |
| `Retencion_%_PY` | Tasa de retención del año anterior. | 3 | [retencion_pct_py.dax](Medidas_Rate/retencion_pct_py.dax) |
| `Churn_%_vs_PY_(texto)` | Texto con flecha para la tarjeta de churn, en PUNTOS PORCENTUALES. | 3 | [churn_pct_vs_py_texto.dax](Medidas_Rate/churn_pct_vs_py_texto.dax) |
| `Retencion_%_vs_PY_texto` | Texto con flecha para la tarjeta de retención, en puntos porcentuales. | 3 | [retencion_pct_vs_py_texto.dax](Medidas_Rate/retencion_pct_vs_py_texto.dax) |
| `ultima_compra_a_fecha_PY` | Última compra del cliente HASTA el corte del año anterior (lo que se sabía ese día). | 3 | [ultima_compra_a_fecha_py.dax](Medidas_Rate/ultima_compra_a_fecha_py.dax) |

## Medidas_Clientes_Activos

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `Clientes_Activos_LY` | Clientes activos del año anterior (recencia < umbral al corte PY). | 3 | [clientes_activos_ly.dax](Medidas_Clientes_Activos/clientes_activos_ly.dax) |
| `Clientes_Activos_vs_LY_%` | Variación relativa de clientes activos contra el año anterior. | 3 | [clientes_activos_vs_ly_pct.dax](Medidas_Clientes_Activos/clientes_activos_vs_ly_pct.dax) |
| `Clientes_Totales_Vs_PY_%` | Variación relativa de clientes totales contra el año anterior (+7.5 % en el panel). | 3 | [clientes_totales_vs_py_pct.dax](Medidas_Clientes_Activos/clientes_totales_vs_py_pct.dax) |
| `Clientes_Activos_vs_LY_%_texto` | Texto con flecha para la tarjeta de clientes activos. | 3 | [clientes_activos_vs_ly_pct_texto.dax](Medidas_Clientes_Activos/clientes_activos_vs_ly_pct_texto.dax) |
| `Clientes_Totales_Vs_PY_texto` | Texto con flecha para la tarjeta de clientes ("🔺 7.5 % vs PY"). | 3 | [clientes_totales_vs_py_texto.dax](Medidas_Clientes_Activos/clientes_totales_vs_py_texto.dax) |

## Medidas_Serie

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `Clientes_Totales_(serie)` | Universo de clientes al corte de cada punto del eje (mes, trimestre...). Alimenta los minigráficos. | 3 | [clientes_totales_serie.dax](Medidas_Serie/clientes_totales_serie.dax) |
| `Clientes_Inactivos_(serie)` | Clientes inactivos al corte de cada punto del eje. Alimenta "Clientes inactivos". | 3 | [clientes_inactivos_serie.dax](Medidas_Serie/clientes_inactivos_serie.dax) |
| `Churn_%_(serie)` | Churn punto por punto en la gráfica. Devuelve vacío en los periodos posteriores a la última venta. | 3 | [churn_pct_serie.dax](Medidas_Serie/churn_pct_serie.dax) |
| `Retencion_%_(serie)` | Retención punto por punto. En el .pbix puede conservar el nombre antiguo Retencion_%_vs_PY_(texto), que no era un texto ni comparaba con el año anterior; conviene renombrarla. | 3 | [retencion_pct_serie.dax](Medidas_Serie/retencion_pct_serie.dax) |

## Medidas_Reactivacion

| Medida | Qué hace | Paneles | Archivo |
|---|---|---|---|
| `Gap_vs_umbral_(dias)` | Días que el cliente lleva por encima del umbral. Menor gap = cruzó hace poco = más fácil de reactivar. | 4 | [gap_vs_umbral_dias.dax](Medidas_Reactivacion/gap_vs_umbral_dias.dax) |
| `Monetary_12m` | Valor (con IVA) comprado por el cliente en los 12 meses anteriores a Fecha_Ref. | 4 | [monetary_12m.dax](Medidas_Reactivacion/monetary_12m.dax) |
| `Ranking_Reactivacion_(rapido)` | Prioridad por cercanía: 1 = el cliente que cruzó el umbral más recientemente. | 4 | [ranking_reactivacion_rapido.dax](Medidas_Reactivacion/ranking_reactivacion_rapido.dax) |
| `Ranking_Reactivacion_(valor 12m)` | Prioridad por valor: 1 = el cliente en churn que más compró en los últimos 12 meses. | 4 | [ranking_reactivacion_valor_12m.dax](Medidas_Reactivacion/ranking_reactivacion_valor_12m.dax) |
| `Segmento_Reactivacion` | Clasifica a cada cliente: Activo, Valor reciente + Fácil, Valor reciente, Dormido reciente, Dormido crónico (+24M). | 4 | [segmento_reactivacion.dax](Medidas_Reactivacion/segmento_reactivacion.dax) |
| `Filtro_Segmento_Reactivacion` | Devuelve 1 si el cliente pertenece al segmento elegido en el segmentador (0 si no). Se pone en "Filtros de este visual" con valor 1. | 4 | [filtro_segmento_reactivacion.dax](Medidas_Reactivacion/filtro_segmento_reactivacion.dax) |
| `Clientes_por_segmento` | Cuántos clientes hay en cada segmento (la fila de total suma 172). | 4 | [clientes_por_segmento.dax](Medidas_Reactivacion/clientes_por_segmento.dax) |
| `Base_en_riesgo_12M` | Compras de los últimos 12 meses de los clientes en churn que sí compraron (29 clientes: $200,78 mil). | 4 | [base_en_riesgo_12m.dax](Medidas_Reactivacion/base_en_riesgo_12m.dax) |
| `Ingreso_Recuperable_12M` | Base en riesgo x tasa de conversión. Es un SUPUESTO ajustable ($60,24 mil al 30 %). | 4 | [ingreso_recuperable_12m.dax](Medidas_Reactivacion/ingreso_recuperable_12m.dax) |
| `Valor_Recuperable_Potencial` | Ingreso recuperable x margen ($12,05 mil al 20 %). Es el tope de lo que conviene invertir. | 4 | [valor_recuperable_potencial.dax](Medidas_Reactivacion/valor_recuperable_potencial.dax) |
| `Clientes_convertidos_Esperados` | Clientes que se espera recuperar = clientes objetivo (churn con compras en 12 meses) x conversión: 29 x 30 % = 8.7. | 4 | [clientes_convertidos_esperados.dax](Medidas_Reactivacion/clientes_convertidos_esperados.dax) |
| `CPA_Maximo_permitido_(break_even)` | Costo máximo por cliente recuperado para no perder dinero: valor recuperable / clientes esperados (~$1,38 mil). | 4 | [cpa_maximo_permitido_break_even.dax](Medidas_Reactivacion/cpa_maximo_permitido_break_even.dax) |

## Orden de dependencias del churn (léelo de abajo hacia arriba)

```
Fecha_Ref -> ultima_compra_cliente -> Recency_(dias) -> churn_flag
          -> clientes_con_churn -> churn_% -> Retencion_%
```

La reactivación se apoya en esa cadena: `Gap_vs_umbral_(dias)` y `Monetary_12m` alimentan los rankings y el segmento; el segmento y la base en riesgo alimentan los KPI de ROI.
