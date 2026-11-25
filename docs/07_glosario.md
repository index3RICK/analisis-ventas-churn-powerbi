# 9. Glosario

| Término | Significado |
|---|---|
| **Churn (abandono)** | Proporción de clientes que dejaron de comprar según un criterio definido (aquí: ≥ umbral de días sin compra). |
| **Retención** | Proporción de clientes que siguen comprando: 1 − churn. |
| **RFM** | Recencia, Frecuencia y Monto: tres variables para describir a un cliente. |
| **Recencia** | Días desde la última compra hasta la fecha de referencia. |
| **Umbral** | Número de días sin comprar a partir del cual un cliente se considera en churn. |
| **Fecha de referencia** | Fecha "de corte" con la que se miden recencia y churn. |
| **PY / LY** | *Previous Year* / *Last Year*: año anterior. |
| **YoY / MoM** | *Year over Year* / *Month over Month*: variación contra el año / mes anterior. |
| **pp (puntos porcentuales)** | Unidad para diferencias entre porcentajes (de 90 % a 93 % son +3 pp). |
| **Tabla de hechos** | Tabla con los eventos medibles (ventas); una fila por evento. |
| **Dimensión** | Tabla descriptiva (clientes, productos, fechas) que sirve para filtrar y agrupar. |
| **Esquema en estrella** | Modelo con una tabla de hechos al centro y dimensiones alrededor. |
| **Medida** | Cálculo DAX que se evalúa en cada celda del visual según su contexto. |
| **Columna calculada** | Columna que se calcula al cargar el modelo y se guarda en la tabla. |
| **Contexto de filtro** | Conjunto de filtros activos al evaluar una medida. |
| **Contexto de fila** | La fila actual dentro de un iterador o columna calculada. |
| **Transición de contexto** | Conversión de un contexto de fila en filtro (ocurre al llamar una medida dentro de un iterador). |
| **Iterador** | Función que recorre una tabla fila por fila (`SUMX`, `FILTER`, `RANKX`...). |
| **`CALCULATE`** | Función que evalúa una expresión con el contexto de filtro modificado. |
| **`ALL` / `ALLSELECTED` / `ALLEXCEPT`** | Funciones que quitan filtros: todos / los del visual / todos salvo los indicados. |
| **`KEEPFILTERS`** | Añade un filtro sin reemplazar el existente. |
| **Tabla desconectada** | Tabla sin relaciones, usada como parámetro de una segmentación. |
| **Pareto (80/20)** | Análisis que muestra qué parte de los clientes/productos concentra la mayor parte de las ventas. |
| **Cifra de control** | Número conocido y verificado contra otra fuente, usado para comprobar un cálculo. |
| **Reconciliar** | Comparar dos fuentes o cálculos y explicar cualquier diferencia. |
| **Sparkline** | Minigráfico de línea dentro de una tarjeta o tabla. |
| **RLS** | *Row-Level Security*: seguridad por fila; cada usuario ve solo sus datos. |
| **Power Query / M** | Herramienta y lenguaje para extraer y transformar datos antes de modelar. |
| **DAX Studio** | Herramienta externa gratuita para escribir, depurar y medir consultas DAX. |
