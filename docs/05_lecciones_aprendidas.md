# 5. Lecciones aprendidas

Registro de los problemas que encontré mientras construía el proyecto, cómo los diagnostiqué y qué hice para resolverlos.

| # | Lección | Panel |
|---|---|---|
| 1 | La tabla de abandono cambiaba según el día en que se abría (`TODAY()`) | 3 |
| 2 | Un calendario más largo que los datos distorsiona las series | 3 |
| 3 | Las flechas "vs PY" no comparaban nada | 3 |
| 4 | `ultima_compra_cliente` ignora la fecha (churn del año anterior) | 3 |
| 5 | Churn de categoría ≠ churn de cliente | 3 |
| 6 | El umbral de 90 días no encaja con el ciclo de compra | 3, 4 |
| 7 | Calidad de datos: una agencia con dos nombres | 1, 2, 3 |
| 8 | Un "error" que no era (el DNI) | — |
| 9 | **Importes 100 veces mayores** (configuración regional) | todos |
| 10 | **Dos totales distintos** (IVA del archivo frente al IVA del modelo) | 1, 2 |
| 11 | **El ranking de valor salía `1, 1, 1...`** | 4 |
| 12 | **Clientes esperados y valor con poblaciones distintas** (CPA) | 4 |
| 13 | **Segmentos imposibles y textos que no coinciden** | 4 |

---

## Lección 1 — La tabla de abandono cambiaba según el día en que se abría

**Síntoma.** La tabla de abandono por categoría mostraba una retención total de 1.16 % y solo 7 categorías con valor mayor a 0. Una captura anterior del mismo reporte, con los mismos datos, mostraba 5.23 % y más categorías con valor (Gabinetes: 13.33 % antes y 0.00 % después).

**Hipótesis descartada.** "La tabla no carga completa". Sí cargaba: estaba ordenada por retención descendente y el resto de categorías valía 0.00 %.

**Causa.** La medida `Fecha_Ref` usaba `TODAY()`:

```dax
Fecha_Ref = MIN( COALESCE(MAX(DIM_Calendario[Fecha]), TODAY()), TODAY() )
```

Las ventas llegan al 5-sep-2025. La captura anterior corresponde a un "hoy" entre el 30-sep y el 4-oct-2025; la nueva, a un "hoy" posterior. Cada día que pasa más clientes cruzan los 90 días desde su última compra, así que el mismo archivo da resultados distintos. Con un "hoy" a partir de diciembre de 2025, **todos** los clientes salen en churn.

**Cómo lo confirmé.** Recalculé churn en pandas con distintas fechas de referencia:

| Fecha de referencia | Retención total | Coincide con |
|---|---|---|
| 30-sep al 4-oct-2025 | 5.23 % (Gabinetes 13.33 %) | La captura anterior, exacta |
| Desde ~18-nov-2025 | 1.16 % (Gabinetes 0.00 %) | La captura nueva, exacta |

**Solución.** Anclar la fecha a la última venta de los datos ([`fecha_ref.dax`](../codigo/dax/Medidas_churn/fecha_ref.dax)):

```dax
Fecha_Ref = 
VAR ult_venta = CALCULATE(MAX(Analisis_Ventas[Fecha]), ALL(Analisis_Ventas))
VAR fin_rango = MAX(DIM_Calendario[Fecha])
RETURN MIN(COALESCE(fin_rango, ult_venta), ult_venta)
```

**Regla general.** Un reporte que cambia de resultado según el día en que se abre, sin que cambien los datos, tiene una dependencia oculta del reloj. En producción esto significa números distintos en dos reuniones seguidas. Si hace falta "hasta hoy", conviene hacerlo explícito (por ejemplo, con un parámetro de fecha visible).

---

## Lección 2 — Un calendario más largo que los datos distorsiona las series

**Síntoma.** Las gráficas de línea mostraban un movimiento brusco al final.

**Causa.** `DIM_Calendario` llegaba hasta `TODAY()`. En los meses posteriores a la última venta nadie compra, así que las medidas de serie veían a todos los clientes cruzar el umbral: churn al alza sin que pasara nada.

**Solución.** Terminar el calendario en el último año con ventas ([`DIM_Calendario.dax`](../codigo/dax/tablas_calculadas/DIM_Calendario.dax)) y devolver `BLANK()` en las medidas de serie cuando todo el periodo es posterior a la última venta ([`churn_pct_serie.dax`](../codigo/dax/Medidas_Serie/churn_pct_serie.dax)).

**Detalle fino.** La condición debe usar `MIN(DIM_Calendario[Fecha])`, no `MAX`. Con un eje mensual, el mes de la última venta (sep-2025) termina el 30-sep, que es posterior al 5-sep; con `MAX` ese mes real también quedaría vacío.

---

## Lección 3 — Las flechas "vs PY" no comparaban nada

**Síntoma.** Las tarjetas mostraban siempre 🔺 y un porcentaje que parecía el valor del año anterior.

**Causa.** En `Churn_%_vs_PY_(Texto)` y `Retencion_%_vs_PY_texto` la flecha se decidía con `IF(d >= 0, ...)` donde `d` es el valor del **año anterior** (un porcentaje, nunca negativo) y el número mostrado era ese mismo valor, no la variación.

**Solución.** Variación = actual − PY, expresada en **puntos porcentuales** (pp):

```dax
VAR delta = [churn_%] - [Churn_%_PY]
RETURN IF(delta >= 0, "🔺", "🔻") & " " & FORMAT(ABS(delta) * 100, "0.0") & " pp vs PY"
```

**Estado:** ✅ aplicada y verificada en el reporte (3.5 pp).

**Regla general.** Si una comparación siempre da el mismo signo, no está comparando. Al validar un indicador, prueba con un caso donde sepas qué resultado debe salir. Y para tasas, la variación se expresa en **pp**: de 92.5 % a 89.0 % son −3.5 pp; decir "−3.8 %" se presta a confusión.

---

## Lección 4 — `ultima_compra_cliente` ignora la fecha

`ALL(DIM_Calendario)` quita el filtro de fecha, así que la "última compra" es la de todo el histórico. Para la fecha actual no importa. Para el **año anterior**, el universo se reduce a clientes cuya última compra de toda la vida fue antes del corte PY, y el churn PY se infla: un cliente que compró en 2024 y de nuevo en 2025 desaparece del universo PY.

**Solución aplicada:** `ultima_compra_a_fecha_PY` calcula la última compra *hasta* el corte ([`ultima_compra_a_fecha_py.dax`](../codigo/dax/Medidas_Rate/ultima_compra_a_fecha_py.dax)) y las medidas PY la usan.

| | Primera versión | Versión corregida |
|---|---|---|
| Clientes en el universo PY | 124 | **160** |
| Churn del año anterior (umbral 120) | 91.94 % | **92.50 %** |

Validación independiente: `python codigo/python/validar_churn.py --umbral 120 --modo correcto`. Con la versión corregida, la tarjeta de clientes pasó a **+7.5 %** frente al año anterior.

---

## Lección 5 — Churn de categoría vs churn de cliente

Ver [`04_churn_y_rfm_explicado.md`](04_churn_y_rfm_explicado.md). Moraleja: define el nombre de la métrica según lo que mide realmente.

---

## Lección 6 — El umbral de 90 días no encaja con el ciclo de compra

Ver [`04_churn_y_rfm_explicado.md`](04_churn_y_rfm_explicado.md). La mediana entre compras es de ~22 meses. Con 90 días, 90.7 % de los clientes aparece como "abandono"; con 120, 88.95 %; con 180, 83.1 %. Dominar la técnica no sustituye preguntarse si los parámetros tienen sentido para los datos. El panel final usa 120 días, pero el umbral es un control editable.

---

## Lección 7 — Calidad de datos: una agencia con dos nombres

La revisión automática detectó que `Tech DCM Barcelona` aparecía en 221 filas de ventas (23 %) pero no en `DIM_Agencias`: cualquier visual por agencia dejaba esas filas sin clasificar.

**Resolución.** Era la agencia Norte con otro nombre. Se corrigió en Power Query (`Tech DCM Barcelona` → `Tech BCN Norte`, ver [`Analisis_Ventas.m`](../codigo/powerquery/Analisis_Ventas.m)) y ahora hay 3 agencias. Resultado: Norte pasó a **43.68 %** del importe (≈ 20 % + ≈ 23 % que estaban separadas). Los scripts de Python pueden simularlo con `--corregir-agencias`.

También: un guion no estándar (U+2011) en 10 filas de `Access Points Wi‑Fi` rompe cualquier relación o filtro por **nombre**; por eso se relaciona por **código**.

---

## Lección 8 — Corrección sobre un "error" que no era

Al revisar los datos pegados a mano en el chat apareció un DNI con 9 dígitos en vez de 10. Al compararlo con el archivo de origen resultó ser un error de transcripción al pegar (el dato original está bien). Aprendizaje: **antes de reportar un error de datos, compáralo contra la fuente**, no contra una copia.

---

## Lección 9 — Los importes salían 100 veces más grandes

**Síntoma.** La tarjeta de facturación mostraba **$219,15 mill.**; la suma real del archivo es de 2.19 millones.

**Pista.** El número era *exactamente* 100 veces la cifra de control. Un error que es un múltiplo exacto (×10, ×100, ×1000) casi siempre es un problema de **formato de números**, no de lógica. En Power Query, `Precio` aparecía como `12.443,00` cuando el valor original era `$124.43`.

**Causa.** El paso "Tipo cambiado" convertía el texto `"$124.43"` a `Currency.Type` con la configuración regional del equipo, donde el punto es separador de **miles**. `124.43` se leyó como 12,443. Todos los precios del archivo usan punto decimal y ninguno trae comas.

**Cómo se confirmó.** Al comparar contra el archivo de origen en pandas: mismo patrón en todas las filas, y todos los importes del reporte eran exactamente ×100.

**Solución.** Sacar `Precio` y `Total` del paso original (dejarlas como texto) y convertirlas en un paso aparte con la configuración regional correcta:

```m
Table.TransformColumnTypes(#"Tipo cambiado", {{"Precio", Currency.Type}, {"Total", Currency.Type}}, "en-US")
```

**Ojo.** No se debe aplicar `"en-US"` a toda la tabla: `Fecha` (`01-05-2018`) es día-mes-año, y con `en-US` se leería como 5 de enero. **Cada columna con su propia configuración regional.**

**Reglas generales.**
1. Antes de construir medidas, compara una cifra de control del archivo de origen contra Power BI.
2. Desconfía de una cifra que sale múltiplo exacto de otra.
3. El mismo texto se lee distinto según la configuración regional: el mismo archivo puede dar cifras distintas en otra computadora.

---

## Lección 10 — Dos totales distintos: el IVA del archivo y el del modelo

**Síntoma.** Con los importes ya corregidos, "Facturación" mostraba **2,19 millones** y "Ventas Globales" **2,08 millones**.

**Causa.** El archivo original trae IVA del **21 %** (España) y la columna `Total` ya calculada con él: 1,811,167.84 × 1.21 = 2,191,513.09. En el modelo, el IVA se cambió **a propósito al 15 %** (Ecuador) en Power Query, de modo que la medida `ventas_totales` da 1,811,167.84 × 1.15 = **2,082,843.02**. Una tarjeta sumaba la columna `Total` (valor fijo del archivo) y la otra la medida (que se recalcula con las reglas del modelo).

**Pista que lo delató.** Todos los clientes estaban un 4.96 % por debajo de mi cálculo; no era una pérdida de filas sino un factor uniforme (115/121 = 0.9504).

**Solución.** Usar siempre `[ventas_totales]` y **quitar la columna `Total`** del modelo, para que no se use por error.

**Regla general.** Una columna precalculada es un valor fijo; una medida se recalcula. Si dos fuentes deberían decir lo mismo y no coinciden, hay que decidir cuál manda y eliminar la otra.

---

## Lección 11 — El ranking de valor salía `1, 1, 1...`

**Síntoma.** En la tabla de reactivación, `Ranking_Reactivacion_(valor 12m)` daba 1 a todos los clientes aunque sus importes eran distintos.

**Causa.** La medida iteraba sobre `ALLSELECTED(Analisis_Ventas[Cliente])`, pero la tabla muestra `DIM_Clientes[Cliente]`. El filtro de cada fila viaja de la dimensión a la tabla de hechos y deja a cada cliente **solo en su propia lista**; `RANKX` lo compara contra sí mismo y siempre da 1. La medida hermana (`rapido`) sí funcionaba porque usaba `DIM_Clientes[Cliente]`.

**Solución.** Iterar sobre la misma columna que muestra la tabla ([`ranking_reactivacion_valor_12m.dax`](../codigo/dax/Medidas_Reactivacion/ranking_reactivacion_valor_12m.dax)). Resultado: Aitana Valdevas 1, Nora Campos 2, Víctor Mora 3...

**Regla general.** Con `ALLSELECTED` o `ALL`, conviene usar la columna que realmente se ve en el visual. Una columna de otra tabla no siempre elimina el filtro de la fila.

---

## Lección 12 — Clientes esperados y valor con poblaciones distintas

**Síntoma.** La primera versión mostraba 49 clientes convertidos esperados; con la corrección, 9.

**Causa.** La medida original multiplicaba la conversión por **todos** los clientes en churn (153 × 30 % = 46), pero el dinero de la base (`Base_en_riesgo_12M`) solo incluía a los 29 que compraron en los últimos 12 meses. Se dividía el valor de 29 clientes entre los clientes esperados de 153: el CPA máximo salía ≈ 5 veces más bajo (≈ $263 en lugar de ≈ $1,38 mil).

**Solución.** Misma población en numerador y denominador: 29 × 30 % = **8.7 ≈ 9** ([`clientes_convertidos_esperados.dax`](../codigo/dax/Medidas_Reactivacion/clientes_convertidos_esperados.dax)).

**Cómo explicarlo.** No es un error de cálculo sino otra definición. En una reunión: "ajusté el cálculo para que numerador y denominador usen la misma población".

**Dato útil.** Con esta definición, el CPA máximo = base × margen ÷ clientes objetivo; **no depende de la tasa de conversión** (se cancela). La conversión solo cambia *cuántos* clientes se recuperan.

---

## Lección 13 — Segmentos imposibles y textos que no coinciden

**Segmento que nunca aparecía.** `Dormido reciente` valía siempre 0. Quien no tiene compras en los últimos 12 meses tiene recencia ≥ 365 días, así que la regla "recencia ≥ 365 = dormido crónico" absorbía a todos. **Solución:** cortar el dormido a 24 meses (≈ la mediana entre compras): 27 dormidos recientes y 97 crónicos.

**Segmentador que no devolvía nada.** Al elegir "Dormido crónico" salía una tabla vacía. El texto de la tabla del segmentador decía `(+12M)` y la medida devolvía `(+24M)`. Un segmentador sobre una tabla desconectada compara **texto**, y debe ser idéntico (mayúsculas, tildes, espacios, paréntesis).

**Fila de total.** El total mostraba "Activo" y un conteo absurdo; se protegió con `HASONEVALUE`.

**Regla general.** Cuando un filtro "no encuentra nada", la primera pregunta es: ¿el valor que filtro es idéntico al valor que calcula la medida?

---

## Lo que haría distinto

1. Revisar la calidad de los datos **antes** de escribir una sola medida, y comparar un total de control contra el archivo de origen (lecciones 9 y 10).
2. No usar `TODAY()` en un modelo analítico sin un motivo explícito.
3. Validar cada KPI clave contra una segunda fuente (aquí, pandas y SQL).
4. Poner un nombre honesto a cada métrica (churn de categoría ≠ churn de cliente).
5. Revisar los tipos de dato y la configuración regional de las columnas de dinero y de fecha después de importar.
6. Documentar las definiciones **dentro** del reporte y los supuestos junto a cada cifra.
