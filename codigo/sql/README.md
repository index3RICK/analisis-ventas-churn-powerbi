# SQL

## `churn_por_categoria.sql`

Churn y retención por categoría, equivalente a la tabla del panel de abandono de Power BI. Usa CTE (`WITH`), `GROUP BY` y agregación condicional (`SUM(CASE WHEN ...)`).

- **Motor probado:** SQLite (vía `codigo/python/ejecutar_sql.py`).
- **Parámetros:** `:fecha_ref` (AAAA-MM-DD) y `:umbral` (días).
- **Lógica:** "a la fecha" (modo `correcto` de `codigo/python/churn.py`).

```bash
python codigo/python/ejecutar_sql.py --fecha-ref 2025-09-05 --umbral 120 --comparar
```

La opción `--comparar` verifica que SQL y pandas dan el mismo resultado en todas las categorías.

## Adaptar a otros motores

| Motor | Diferencia de días |
|---|---|
| SQL Server | `DATEDIFF(DAY, ultima_compra, @fecha_ref)` |
| PostgreSQL | `(fecha_ref::date - ultima_compra::date)` |
| BigQuery | `DATE_DIFF(DATE(@fecha_ref), ultima_compra, DAY)` |

Los parámetros con nombre cambian de sintaxis (`:p` en SQLite, `@p` en SQL Server/BigQuery, `%(p)s` en psycopg2).

## Ampliaciones posibles

1. Añadir el churn del año anterior (otra fecha de corte) en la misma consulta con un segundo CTE.
2. Calcular el churn por `tipocliente` en lugar de por categoría.
3. Usar una función de ventana (`LAG`) para calcular los días entre compras consecutivas de cada cliente (es lo que respalda el hallazgo de los ~669 días de mediana).
4. Calcular el Pareto de clientes con `SUM(...) OVER (ORDER BY ...)`.

