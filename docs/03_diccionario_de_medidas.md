# 3. Diccionario de medidas

Catálogo de las **63 medidas** del reporte final, organizado **por panel**. Cada una tiene su propio archivo con el código y comentarios en español en [`codigo/dax/`](../codigo/dax/README.md).

**Cifras de control** (sin filtros, IVA 15 %): `ventas_netas` = 1,811,167.84 · `iva_usd` = 271,675.18 · `ventas_totales` = **2,082,843.02**.

> El archivo original traía IVA 21 % (total 2,191,513.09). El modelo usa 15 % (Ecuador); ver [lecciones aprendidas](05_lecciones_aprendidas.md).

Una medida puede aparecer en varios paneles.

## Panel 1 — Cuadro de mando

| Medida | Tabla de medidas | Qué responde |
|---|---|---|
| [`importe_bruto`](../codigo/dax/Medidas_base_facturacion/importe_bruto.dax) | `Medidas_base_facturacion` | Lo que se habría cobrado sin descuentos: Precio x Cantidad, calculado fila por fila y luego sumado. |
| [`descuento_usd`](../codigo/dax/Medidas_base_facturacion/descuento_usd.dax) | `Medidas_base_facturacion` | Dinero descontado: Precio x Cantidad x Descuento, fila por fila. |
| [`ventas_netas`](../codigo/dax/Medidas_base_facturacion/ventas_netas.dax) | `Medidas_base_facturacion` | Venta después de descuentos y antes de IVA. |
| [`iva_usd`](../codigo/dax/Medidas_base_facturacion/iva_usd.dax) | `Medidas_base_facturacion` | IVA cobrado: se aplica sobre el valor ya descontado de cada fila. |
| [`ventas_totales`](../codigo/dax/Medidas_base_facturacion/ventas_totales.dax) | `Medidas_base_facturacion` | Venta total con IVA = ventas_netas + iva_usd. Es la medida principal del proyecto. |
| [`unidades_vendidas`](../codigo/dax/Medidas_base_facturacion/unidades_vendidas.dax) | `Medidas_base_facturacion` | Número de piezas vendidas. |
| [`precio_promedio`](../codigo/dax/Medidas_base_facturacion/precio_promedio.dax) | `Medidas_base_facturacion` | Precio medio por unidad (bruto): importe_bruto / unidades. |
| [`ticket_promedio`](../codigo/dax/Medidas_base_facturacion/ticket_promedio.dax) | `Medidas_base_facturacion` | Venta neta promedio por factura (una factura tiene varias filas). |
| [`numero_clientes_unicos`](../codigo/dax/Medidas_participacion_ranking/numero_clientes_unicos.dax) | `Medidas_participacion_ranking` | Clientes distintos (DISTINCTCOUNT). |

## Panel 2 — Detalle de ventas global

| Medida | Tabla de medidas | Qué responde |
|---|---|---|
| [`importe_bruto`](../codigo/dax/Medidas_base_facturacion/importe_bruto.dax) | `Medidas_base_facturacion` | Lo que se habría cobrado sin descuentos: Precio x Cantidad, calculado fila por fila y luego sumado. |
| [`descuento_usd`](../codigo/dax/Medidas_base_facturacion/descuento_usd.dax) | `Medidas_base_facturacion` | Dinero descontado: Precio x Cantidad x Descuento, fila por fila. |
| [`ventas_netas`](../codigo/dax/Medidas_base_facturacion/ventas_netas.dax) | `Medidas_base_facturacion` | Venta después de descuentos y antes de IVA. |
| [`iva_usd`](../codigo/dax/Medidas_base_facturacion/iva_usd.dax) | `Medidas_base_facturacion` | IVA cobrado: se aplica sobre el valor ya descontado de cada fila. |
| [`ventas_totales`](../codigo/dax/Medidas_base_facturacion/ventas_totales.dax) | `Medidas_base_facturacion` | Venta total con IVA = ventas_netas + iva_usd. Es la medida principal del proyecto. |
| [`ventas_mes_anterior`](../codigo/dax/Medidas_Inteligencia_Tiempo/ventas_mes_anterior.dax) | `Medidas_Inteligencia_Tiempo` | Ventas del mes anterior (desplaza el contexto un mes atrás con DATEADD). |
| [`ventas_totales_ly`](../codigo/dax/Medidas_Inteligencia_Tiempo/ventas_totales_ly.dax) | `Medidas_Inteligencia_Tiempo` | Ventas del mismo periodo del año anterior (SAMEPERIODLASTYEAR). Alimenta "Referencia LY". |
| [`crecimiento_mom`](../codigo/dax/Medidas_Inteligencia_Tiempo/crecimiento_mom.dax) | `Medidas_Inteligencia_Tiempo` | Variación porcentual contra el mes anterior. |
| [`crecimiento_yoy`](../codigo/dax/Medidas_Inteligencia_Tiempo/crecimiento_yoy.dax) | `Medidas_Inteligencia_Tiempo` | Variación porcentual contra el mismo periodo del año anterior. Es el "(%) Creci / Decre". |
| [`numero_clientes_unicos`](../codigo/dax/Medidas_participacion_ranking/numero_clientes_unicos.dax) | `Medidas_participacion_ranking` | Clientes distintos (DISTINCTCOUNT). |
| [`%_participacion_cliente`](../codigo/dax/Medidas_participacion_ranking/pct_participacion_cliente.dax) | `Medidas_participacion_ranking` | % de clientes sobre el total absoluto (ALL: ignora segmentadores). |
| [`%_participacion_ventas`](../codigo/dax/Medidas_participacion_ranking/pct_participacion_ventas.dax) | `Medidas_participacion_ranking` | % de ventas sobre lo que el usuario está viendo (ALLSELECTED). |
| [`ranking_venta_clientes`](../codigo/dax/Medidas_participacion_ranking/ranking_venta_clientes.dax) | `Medidas_participacion_ranking` | Posición de cada cliente por ventas (1 = el que más compra). |
| [`ranking_ventas_vendedor`](../codigo/dax/Medidas_participacion_ranking/ranking_ventas_vendedor.dax) | `Medidas_participacion_ranking` | Posición de cada vendedor por ventas. |
| [`acum_ventas_cliente`](../codigo/dax/Medidas_participacion_ranking/acum_ventas_cliente.dax) | `Medidas_participacion_ranking` | Venta acumulada de los clientes hasta la posición actual (base del Pareto). |
| [`acum_ventas_vendedor`](../codigo/dax/Medidas_participacion_ranking/acum_ventas_vendedor.dax) | `Medidas_participacion_ranking` | Venta acumulada de los vendedores hasta la posición actual. |
| [`%_acum_pareto_clientes`](../codigo/dax/Medidas_participacion_ranking/pct_acum_pareto_clientes.dax) | `Medidas_participacion_ranking` | % acumulado de la venta por cliente (curva 80/20). |
| [`%_acum_pareto_vendedor`](../codigo/dax/Medidas_participacion_ranking/pct_acum_pareto_vendedor.dax) | `Medidas_participacion_ranking` | % acumulado de la venta por vendedor. Es la barra de "Fuerza de ventas (Ejecutivo)". |

## Panel 3 — Abandono de clientes

| Medida | Tabla de medidas | Qué responde |
|---|---|---|
| [`ventas_totales`](../codigo/dax/Medidas_base_facturacion/ventas_totales.dax) | `Medidas_base_facturacion` | Venta total con IVA = ventas_netas + iva_usd. Es la medida principal del proyecto. |
| [`Fecha_Ref`](../codigo/dax/Medidas_churn/fecha_ref.dax) | `Medidas_churn` | Fecha de corte del análisis. Nunca pasa de la última venta real. |
| [`churn_umbral_dias_value`](../codigo/dax/Medidas_churn/churn_umbral_dias_value.dax) | `Medidas_churn` | Umbral elegido en el control "Umbral" (días sin comprar = abandono). |
| [`ultima_compra_cliente`](../codigo/dax/Medidas_churn/ultima_compra_cliente.dax) | `Medidas_churn` | Fecha de la última compra de cada cliente, ignorando el filtro de fecha. |
| [`Recency_(dias)`](../codigo/dax/Medidas_churn/recency_dias.dax) | `Medidas_churn` | R de RFM: días desde la última compra hasta Fecha_Ref. |
| [`churn_flag`](../codigo/dax/Medidas_churn/churn_flag.dax) | `Medidas_churn` | 1 si el cliente está en churn (recencia >= umbral), 0 si está activo. Se evalúa cliente por cliente. |
| [`clientes_totales`](../codigo/dax/Medidas_churn/clientes_totales.dax) | `Medidas_churn` | Clientes que han comprado alguna vez hasta la fecha de referencia. |
| [`clientes_con_churn`](../codigo/dax/Medidas_churn/clientes_con_churn.dax) | `Medidas_churn` | Suma de los churn_flag = clientes en abandono. |
| [`clientes_activos`](../codigo/dax/Medidas_churn/clientes_activos.dax) | `Medidas_churn` | clientes_totales - clientes_con_churn. |
| [`churn_%`](../codigo/dax/Medidas_churn/churn_pct.dax) | `Medidas_churn` | Porcentaje de abandono = clientes_con_churn / clientes_totales. |
| [`Retencion_%`](../codigo/dax/Medidas_churn/retencion_pct.dax) | `Medidas_churn` | 1 - churn_%. Devuelve BLANK si no hay clientes. |
| [`Frecuency_Facturas`](../codigo/dax/Medidas_churn/frecuency_facturas.dax) | `Medidas_churn` | F de RFM: facturas distintas hasta la fecha de referencia. |
| [`Monetary_Ventas`](../codigo/dax/Medidas_churn/monetary_ventas.dax) | `Medidas_churn` | M de RFM: valor comprado hasta la fecha de referencia. |
| [`Fecha_Ref_PY`](../codigo/dax/Medidas_Rate/fecha_ref_py.dax) | `Medidas_Rate` | Fecha de corte del año anterior: la misma fecha, 12 meses atrás (EDATE). |
| [`Clientes_totales_PY`](../codigo/dax/Medidas_Rate/clientes_totales_py.dax) | `Medidas_Rate` | Clientes que ya habían comprado al corte del año anterior. |
| [`Clientes_con_Churn_PY`](../codigo/dax/Medidas_Rate/clientes_con_churn_py.dax) | `Medidas_Rate` | Clientes en churn al corte del año anterior. |
| [`Clientes_Activo_PY`](../codigo/dax/Medidas_Rate/clientes_activo_py.dax) | `Medidas_Rate` | Clientes activos al corte del año anterior = totales PY - churn PY. |
| [`Churn_%_PY`](../codigo/dax/Medidas_Rate/churn_pct_py.dax) | `Medidas_Rate` | Tasa de churn del año anterior. Con el panel final (umbral 120): 91.94 %. |
| [`Retencion_%_PY`](../codigo/dax/Medidas_Rate/retencion_pct_py.dax) | `Medidas_Rate` | Tasa de retención del año anterior. |
| [`Clientes_Activos_LY`](../codigo/dax/Medidas_Clientes_Activos/clientes_activos_ly.dax) | `Medidas_Clientes_Activos` | Clientes activos del año anterior (recencia < umbral al corte PY). |
| [`Clientes_Activos_vs_LY_%`](../codigo/dax/Medidas_Clientes_Activos/clientes_activos_vs_ly_pct.dax) | `Medidas_Clientes_Activos` | Variación relativa de clientes activos contra el año anterior. |
| [`Clientes_Totales_Vs_PY_%`](../codigo/dax/Medidas_Clientes_Activos/clientes_totales_vs_py_pct.dax) | `Medidas_Clientes_Activos` | Variación relativa de clientes totales contra el año anterior (+7.5 % en el panel). |
| [`Clientes_Activos_vs_LY_%_texto`](../codigo/dax/Medidas_Clientes_Activos/clientes_activos_vs_ly_pct_texto.dax) | `Medidas_Clientes_Activos` | Texto con flecha para la tarjeta de clientes activos. |
| [`Clientes_Totales_Vs_PY_texto`](../codigo/dax/Medidas_Clientes_Activos/clientes_totales_vs_py_texto.dax) | `Medidas_Clientes_Activos` | Texto con flecha para la tarjeta de clientes ("🔺 7.5 % vs PY"). |
| [`Churn_%_vs_PY_(texto)`](../codigo/dax/Medidas_Rate/churn_pct_vs_py_texto.dax) | `Medidas_Rate` | Texto con flecha para la tarjeta de churn, en PUNTOS PORCENTUALES. |
| [`Retencion_%_vs_PY_texto`](../codigo/dax/Medidas_Rate/retencion_pct_vs_py_texto.dax) | `Medidas_Rate` | Texto con flecha para la tarjeta de retención, en puntos porcentuales. |
| [`ultima_compra_a_fecha_PY`](../codigo/dax/Medidas_Rate/ultima_compra_a_fecha_py.dax) | `Medidas_Rate` | Última compra del cliente HASTA el corte del año anterior (lo que se sabía ese día). |
| [`Clientes_Totales_(serie)`](../codigo/dax/Medidas_Serie/clientes_totales_serie.dax) | `Medidas_Serie` | Universo de clientes al corte de cada punto del eje (mes, trimestre...). Alimenta los minigráficos. |
| [`Clientes_Inactivos_(serie)`](../codigo/dax/Medidas_Serie/clientes_inactivos_serie.dax) | `Medidas_Serie` | Clientes inactivos al corte de cada punto del eje. Alimenta "Clientes inactivos". |
| [`Churn_%_(serie)`](../codigo/dax/Medidas_Serie/churn_pct_serie.dax) | `Medidas_Serie` | Churn punto por punto en la gráfica. Devuelve vacío en los periodos posteriores a la última venta. |
| [`Retencion_%_(serie)`](../codigo/dax/Medidas_Serie/retencion_pct_serie.dax) | `Medidas_Serie` | Retención punto por punto. En el .pbix puede conservar el nombre antiguo Retencion_%_vs_PY_(texto), que no era un texto ni comparaba con el año anterior; conviene renombrarla. |
| [`ventas_totales_ly`](../codigo/dax/Medidas_Inteligencia_Tiempo/ventas_totales_ly.dax) | `Medidas_Inteligencia_Tiempo` | Ventas del mismo periodo del año anterior (SAMEPERIODLASTYEAR). Alimenta "Referencia LY". |

## Panel 4 — Reactivación de clientes

| Medida | Tabla de medidas | Qué responde |
|---|---|---|
| [`ventas_totales`](../codigo/dax/Medidas_base_facturacion/ventas_totales.dax) | `Medidas_base_facturacion` | Venta total con IVA = ventas_netas + iva_usd. Es la medida principal del proyecto. |
| [`Fecha_Ref`](../codigo/dax/Medidas_churn/fecha_ref.dax) | `Medidas_churn` | Fecha de corte del análisis. Nunca pasa de la última venta real. |
| [`churn_umbral_dias_value`](../codigo/dax/Medidas_churn/churn_umbral_dias_value.dax) | `Medidas_churn` | Umbral elegido en el control "Umbral" (días sin comprar = abandono). |
| [`ultima_compra_cliente`](../codigo/dax/Medidas_churn/ultima_compra_cliente.dax) | `Medidas_churn` | Fecha de la última compra de cada cliente, ignorando el filtro de fecha. |
| [`Recency_(dias)`](../codigo/dax/Medidas_churn/recency_dias.dax) | `Medidas_churn` | R de RFM: días desde la última compra hasta Fecha_Ref. |
| [`churn_flag`](../codigo/dax/Medidas_churn/churn_flag.dax) | `Medidas_churn` | 1 si el cliente está en churn (recencia >= umbral), 0 si está activo. Se evalúa cliente por cliente. |
| [`clientes_totales`](../codigo/dax/Medidas_churn/clientes_totales.dax) | `Medidas_churn` | Clientes que han comprado alguna vez hasta la fecha de referencia. |
| [`clientes_con_churn`](../codigo/dax/Medidas_churn/clientes_con_churn.dax) | `Medidas_churn` | Suma de los churn_flag = clientes en abandono. |
| [`clientes_activos`](../codigo/dax/Medidas_churn/clientes_activos.dax) | `Medidas_churn` | clientes_totales - clientes_con_churn. |
| [`Gap_vs_umbral_(dias)`](../codigo/dax/Medidas_Reactivacion/gap_vs_umbral_dias.dax) | `Medidas_Reactivacion` | Días que el cliente lleva por encima del umbral. Menor gap = cruzó hace poco = más fácil de reactivar. |
| [`Monetary_12m`](../codigo/dax/Medidas_Reactivacion/monetary_12m.dax) | `Medidas_Reactivacion` | Valor (con IVA) comprado por el cliente en los 12 meses anteriores a Fecha_Ref. |
| [`Ranking_Reactivacion_(rapido)`](../codigo/dax/Medidas_Reactivacion/ranking_reactivacion_rapido.dax) | `Medidas_Reactivacion` | Prioridad por cercanía: 1 = el cliente que cruzó el umbral más recientemente. |
| [`Ranking_Reactivacion_(valor 12m)`](../codigo/dax/Medidas_Reactivacion/ranking_reactivacion_valor_12m.dax) | `Medidas_Reactivacion` | Prioridad por valor: 1 = el cliente en churn que más compró en los últimos 12 meses. |
| [`Segmento_Reactivacion`](../codigo/dax/Medidas_Reactivacion/segmento_reactivacion.dax) | `Medidas_Reactivacion` | Clasifica a cada cliente: Activo, Valor reciente + Fácil, Valor reciente, Dormido reciente, Dormido crónico (+24M). |
| [`Filtro_Segmento_Reactivacion`](../codigo/dax/Medidas_Reactivacion/filtro_segmento_reactivacion.dax) | `Medidas_Reactivacion` | Devuelve 1 si el cliente pertenece al segmento elegido en el segmentador (0 si no). Se pone en "Filtros de este visual" con valor 1. |
| [`Clientes_por_segmento`](../codigo/dax/Medidas_Reactivacion/clientes_por_segmento.dax) | `Medidas_Reactivacion` | Cuántos clientes hay en cada segmento (la fila de total suma 172). |
| [`Base_en_riesgo_12M`](../codigo/dax/Medidas_Reactivacion/base_en_riesgo_12m.dax) | `Medidas_Reactivacion` | Compras de los últimos 12 meses de los clientes en churn que sí compraron (29 clientes: $200,78 mil). |
| [`Ingreso_Recuperable_12M`](../codigo/dax/Medidas_Reactivacion/ingreso_recuperable_12m.dax) | `Medidas_Reactivacion` | Base en riesgo x tasa de conversión. Es un SUPUESTO ajustable ($60,24 mil al 30 %). |
| [`Valor_Recuperable_Potencial`](../codigo/dax/Medidas_Reactivacion/valor_recuperable_potencial.dax) | `Medidas_Reactivacion` | Ingreso recuperable x margen ($12,05 mil al 20 %). Es el tope de lo que conviene invertir. |
| [`Clientes_convertidos_Esperados`](../codigo/dax/Medidas_Reactivacion/clientes_convertidos_esperados.dax) | `Medidas_Reactivacion` | Clientes que se espera recuperar = clientes objetivo (churn con compras en 12 meses) x conversión: 29 x 30 % = 8.7. |
| [`CPA_Maximo_permitido_(break_even)`](../codigo/dax/Medidas_Reactivacion/cpa_maximo_permitido_break_even.dax) | `Medidas_Reactivacion` | Costo máximo por cliente recuperado para no perder dinero: valor recuperable / clientes esperados (~$1,38 mil). |

## Convenciones de nombres sugeridas

Para un proyecto nuevo: `snake_case` sin acentos, sufijos consistentes (`_pct`, `_py`, `_ly`, `_serie`, `_texto`), una tabla de medidas por tema y **un solo estilo** de mayúsculas. Inconsistencias de este proyecto que conviene evitar: `Clientes_Activo_Py` frente a `Clientes_Activo_PY`, `Churn_%_PY` junto a `churn_%`, o una medida llamada `Retencion_%_vs_PY_(texto)` que en realidad era la retención de la serie.
