-- =====================================================================
-- churn_por_categoria.sql
-- Churn y retención por categoría, equivalente a la tabla del panel
-- "Abandono de Clientes" de Power BI.
--
-- Compatible con SQLite (probado) y fácil de adaptar a SQL Server,
-- PostgreSQL o BigQuery (ver notas al final).
--
-- Parámetros (se reciben con nombre):
--   :fecha_ref  fecha de corte en formato 'AAAA-MM-DD'
--   :umbral     días sin comprar para considerar churn (ej. 90)
--
-- Tabla esperada: ventas(Cliente, Fecha, codigocategoria, categorianombre, ...)
--   con Fecha como texto ISO 'AAAA-MM-DD' (así la comparan bien SQLite y
--   otros motores).
--
-- Lógica (igual que el DAX, modo "correcto", es decir "a la fecha"):
--   1) Para cada cliente y categoría, su última compra hasta :fecha_ref.
--   2) Recencia = días entre :fecha_ref y la última compra.
--   3) Churn = recencia >= :umbral.
--   4) Agregamos por categoría.
-- =====================================================================

WITH ultima_compra AS (
    SELECT
        codigocategoria,
        MIN(categorianombre)  AS categoria,        -- un solo nombre por código
        Cliente,
        MAX(Fecha)            AS ultima_compra
    FROM ventas
    WHERE Fecha <= :fecha_ref                      -- solo compras hasta el corte
    GROUP BY codigocategoria, Cliente
),

con_recencia AS (
    SELECT
        codigocategoria,
        categoria,
        Cliente,
        CAST(julianday(:fecha_ref) - julianday(ultima_compra) AS INTEGER) AS recencia_dias
    FROM ultima_compra
)

SELECT
    categoria,
    COUNT(*)                                                        AS clientes_totales,
    SUM(CASE WHEN recencia_dias >= :umbral THEN 1 ELSE 0 END)       AS clientes_con_churn,
    ROUND(100.0 * SUM(CASE WHEN recencia_dias >= :umbral THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                            AS churn_pct,
    ROUND(100.0 - 100.0 * SUM(CASE WHEN recencia_dias >= :umbral THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                            AS retencion_pct
FROM con_recencia
GROUP BY codigocategoria, categoria
ORDER BY retencion_pct DESC, categoria;

-- ---------------------------------------------------------------------
-- NOTAS PARA ADAPTAR A OTROS MOTORES
--   SQL Server : DATEDIFF(DAY, ultima_compra, @fecha_ref) en lugar de julianday
--   PostgreSQL : (:fecha_ref::date - ultima_compra::date) en lugar de julianday
--   BigQuery   : DATE_DIFF(DATE(@fecha_ref), ultima_compra, DAY)
-- ---------------------------------------------------------------------
