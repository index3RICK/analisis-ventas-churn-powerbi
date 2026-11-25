# Recetario DAX — mis patrones de referencia

Colección de patrones para consultar cuando necesites resolver algo rápido. Cada receta dice **cuándo usarla**, **el código** y **la trampa más común**.

> Las recetas marcadas con 📘 vienen de este proyecto y funcionan en el reporte. Las marcadas con 🧪 son patrones genéricos que uso como punto de partida y siempre valido con un caso hecho a mano.

Los ejemplos suponen: `Analisis_Ventas` (hechos), `DIM_Calendario[Fecha]`, `DIM_Clientes[Cliente]`, `DIM_Categoria[categorianombre]` y la medida base `[ventas_totales]`.

---

## 0. Cómo pensar en DAX (3 ideas)

1. **Contexto de filtro:** cada celda del visual evalúa la medida con filtros distintos. Pregúntate siempre "¿qué filtros hay en esta celda?".
2. **`CALCULATE` cambia el contexto:** añade, quita o reemplaza filtros antes de evaluar.
3. **Iteradores (`SUMX`, `FILTER`, `RANKX`...) recorren fila por fila** y activan la transición de contexto: la fila actual se vuelve filtro.

---

## 1. Medidas básicas

### 📘 Suma de una expresión fila por fila
Cuando el valor depende de varias columnas de la misma fila.
```dax
importe_bruto = SUMX(Analisis_Ventas, Analisis_Ventas[Precio] * Analisis_Ventas[Cantidad])
```
**Trampa:** `SUM(Precio) * SUM(Cantidad)` da otro resultado.

### 📘 División segura
```dax
precio_promedio = DIVIDE([importe_bruto], [unidades_vendidas])
```
**Trampa:** el tercer argumento de `DIVIDE` (valor alterno) es 0 si lo pones; un "0 %" parece dato real. Si no hay base de comparación, mejor `BLANK()` (omite el tercer argumento).

### 🧪 Contar con condición
```dax
clientes_distribuidor = 
CALCULATE(
    DISTINCTCOUNT(Analisis_Ventas[Cliente]),
    DIM_Clientes[tipocliente] = "Distribuidor"
)
```

---

## 2. Participación y ranking

### 📘 % del total visible (`ALLSELECTED`)
```dax
%_participacion_ventas = 
DIVIDE([ventas_totales], CALCULATE([ventas_totales], ALLSELECTED(Analisis_Ventas)))
```
**`ALL` vs `ALLSELECTED`:** `ALL` ignora todo (total absoluto); `ALLSELECTED` respeta las segmentaciones (total de lo que el usuario ve).

### 📘 Ranking
```dax
ranking_venta_clientes = RANKX(ALLSELECTED(Analisis_Ventas[Cliente]), [ventas_totales], , DESC)
```

### 📘 Pareto (80/20)
Ver [`codigo/dax/Medidas_participacion_ranking/`](../codigo/dax/Medidas_participacion_ranking/). Pasos: ranking → acumulado hasta ese ranking → % acumulado.

### 🧪 Top N dinámico
```dax
ventas_top5_categorias = 
CALCULATE(
    [ventas_totales],
    FILTER(
        VALUES(DIM_Categoria[categorianombre]),
        RANKX(ALLSELECTED(DIM_Categoria[categorianombre]), [ventas_totales]) <= 5
    )
)
```

---

## 3. Inteligencia de tiempo

**Requisitos:** tabla de fechas continua, marcada como tabla de fechas, relacionada con los hechos; usar siempre `DIM_Calendario[Fecha]`.

### 📘 Mes anterior y mismo periodo del año anterior
```dax
ventas_mes_anterior = CALCULATE([ventas_totales], DATEADD(DIM_Calendario[Fecha], -1, MONTH))
ventas_totales_ly   = CALCULATE([ventas_totales], SAMEPERIODLASTYEAR(DIM_Calendario[Fecha]))
```

### 🧪 Acumulado del año (YTD) y del mes (MTD)
```dax
ventas_ytd = TOTALYTD([ventas_totales], DIM_Calendario[Fecha])
ventas_mtd = TOTALMTD([ventas_totales], DIM_Calendario[Fecha])
```

### 🧪 Acumulado histórico (running total)
```dax
ventas_acumuladas = 
CALCULATE(
    [ventas_totales],
    FILTER(ALL(DIM_Calendario[Fecha]), DIM_Calendario[Fecha] <= MAX(DIM_Calendario[Fecha]))
)
```

### 🧪 Promedio móvil de 3 meses (eje mensual)
```dax
ventas_prom_movil_3m = 
DIVIDE(
    CALCULATE([ventas_totales], DATESINPERIOD(DIM_Calendario[Fecha], MAX(DIM_Calendario[Fecha]), -3, MONTH)),
    3
)
```
**Trampa:** al inicio de la serie hay menos de 3 meses de datos y el promedio queda subestimado.

### 🧪 Primera y última fecha de compra
```dax
primera_compra = CALCULATE(MIN(Analisis_Ventas[Fecha]), ALL(DIM_Calendario))
ultima_compra  = CALCULATE(MAX(Analisis_Ventas[Fecha]), ALL(DIM_Calendario))
```

---

## 4. Clientes: RFM, churn y nuevos

### 📘 Fecha de referencia SIN depender de `TODAY()`
```dax
Fecha_Ref = 
VAR ult_venta = CALCULATE(MAX(Analisis_Ventas[Fecha]), ALL(Analisis_Ventas))
VAR fin_rango = MAX(DIM_Calendario[Fecha])
RETURN MIN(COALESCE(fin_rango, ult_venta), ult_venta)
```

### 📘 Recencia y flag de churn
```dax
Recency_(dias) = 
VAR f_ult = [ultima_compra_cliente]
VAR f_ref = [Fecha_Ref]
RETURN IF(NOT ISBLANK(f_ult) && f_ult <= f_ref, DATEDIFF(f_ult, f_ref, DAY))

churn_flag = 
VAR dias = [Recency_(dias)]
RETURN IF(NOT ISBLANK(dias) && dias >= [churn_umbral_dias_value], 1, 0)
```

### 🧪 Clientes nuevos en el periodo (primera compra dentro del periodo)
```dax
clientes_nuevos = 
VAR ini = MIN(DIM_Calendario[Fecha])
VAR fin = MAX(DIM_Calendario[Fecha])
RETURN
COUNTROWS(
    FILTER(
        VALUES(DIM_Clientes[Cliente]),
        VAR primera = CALCULATE(MIN(Analisis_Ventas[Fecha]), ALL(DIM_Calendario))
        RETURN primera >= ini && primera <= fin
    )
)
```
Clientes recurrentes = clientes con ventas en el periodo − clientes nuevos.

---

## 5. Parámetros y "what-if"

### 📘 Parámetro con tabla desconectada
```dax
Churn_Umbral = GENERATESERIES(15, 180, 15)
churn_umbral_dias_value = SELECTEDVALUE(Churn_Umbral[Churn_Umbral], 90)
```
**Regla:** la tabla NO se relaciona con nada; solo alimenta una segmentación. Usa el **mismo** valor alterno en todas las medidas que la lean.

---

## 6. Presentación

### 🧪 Variación con flecha (en puntos porcentuales)
```dax
churn_vs_py_texto = 
VAR delta = [churn_%] - [Churn_%_PY]
RETURN IF(ISBLANK(delta), BLANK(), IF(delta >= 0, "🔺", "🔻") & " " & FORMAT(ABS(delta) * 100, "0.0") & " pp vs PY")
```
**Trampa clásica:** decidir la flecha con el valor del año anterior en lugar de con la diferencia (ver lección 3).

### 🧪 Semáforo con `SWITCH(TRUE())`
```dax
estado_retencion = 
SWITCH(
    TRUE(),
    ISBLANK([Retencion_%]), BLANK(),
    [Retencion_%] >= 0.60, "Sano",
    [Retencion_%] >= 0.30, "Alerta",
    "Crítico"
)
```
(Los umbrales 60 % y 30 % son de ejemplo; se definen con el negocio.)

### 🧪 Título dinámico
```dax
titulo_ventas = "Ventas de " & SELECTEDVALUE(DIM_Calendario[Año], "todos los años")
```

---

## 7. Errores frecuentes (y cómo detectarlos)

| Síntoma | Causa probable | Qué revisar |
|---|---|---|
| El total no es la suma de las filas | Medida no aditiva (promedios, `DISTINCTCOUNT`, porcentajes) | Es normal; confirma que la medida está bien definida a nivel total |
| Aparece "(En blanco)" en un visual | Valores de la tabla de hechos que no existen en la dimensión | Revisar relaciones y la dimensión (ej. agencia faltante) |
| Resultado cambia según el día | `TODAY()`/`NOW()` en la lógica | Reemplazar por una fecha anclada a los datos |
| `1 - BLANK()` da 100 % | Resta con vacío | `IF(ISBLANK(x), BLANK(), 1 - x)` |
| Inteligencia de tiempo da vacío | Calendario con huecos, sin marcar, o columna de fecha equivocada | Usar `DIM_Calendario[Fecha]` y marcar la tabla de fechas |
| Medida lentísima | Iteradores anidados sobre tablas grandes | Analizador de rendimiento + DAX Studio |
| `>` vs `>=` | Caso del borde | Probar el valor exacto del umbral |
| Un filtro "no hace nada" | La medida usa `ALL`/`REMOVEFILTERS` sobre esa columna | Revisar qué filtros quita |

## 8. Hábitos

1. Escribe primero **la pregunta** en un comentario.
2. Usa `VAR` para nombrar los pasos (se depura más fácil).
3. Prueba con un caso calculado a mano.
4. Comenta el **porqué**, no el qué.
5. Si dudas del resultado, recalcúlalo en Python/SQL (ver [`codigo/python/`](../codigo/python/)).
