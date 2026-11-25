# 4. Churn, retención y RFM explicados

## ¿Qué es el churn?

**Churn** (abandono) es la proporción de clientes que dejaron de comprar. **Retención** es su complemento: la proporción que sigue comprando.

```
churn_%     = clientes que abandonaron / clientes totales
retencion_% = 1 − churn_%
```

El problema real no es la fórmula, sino la pregunta previa: **¿cuándo decimos que alguien "dejó de comprar"?**

## La definición de este proyecto

> Un cliente está en churn si pasaron **N días o más** desde su última compra, medidos hasta una **fecha de referencia**. El panel final usa **N = 120**, ajustable con un control.

Tres decisiones están escondidas ahí, y cada una cambia el resultado:

| Decisión | Valor en este proyecto | Efecto |
|---|---|---|
| Umbral | 120 días (ajustable de 15 a 180) | Más días → menos churn |
| Fecha de referencia | Última venta de los datos | Más tarde → más churn |
| Quién cuenta | Clientes con al menos una compra hasta la fecha de referencia | |

## RFM en una línea

| Letra | Pregunta | Medida |
|---|---|---|
| **R**ecency (recencia) | ¿Hace cuántos días compró por última vez? | `Recency_(dias)` |
| **F**requency (frecuencia) | ¿Cuántas veces compró? | `Frecuency_Facturas` |
| **M**onetary (monto) | ¿Cuánto dinero ha gastado? | `Monetary_Ventas` |

El churn de este proyecto usa solo la **R**. Las otras dos quedan listas para segmentar clientes (por ejemplo, "campeones": compran reciente, seguido y mucho).

## Flujo de cálculo

```
Fecha_Ref ──────────────┐
                        ▼
ultima_compra_cliente → Recency_(dias) → churn_flag (1/0)
                                              │
                                              ▼
                        clientes_con_churn ──► churn_% ──► Retencion_%
                        clientes_totales ────►
```

## Ejemplo trabajado

Fecha de referencia: 5-sep-2025. Umbral: 90 días.

| Cliente | Última compra | Recencia | ¿Churn? |
|---|---|---|---|
| A | 1-sep-2025 | 4 días | No |
| B | 8-jun-2025 | 89 días | No |
| C | 7-jun-2025 | **90 días** | **Sí** (`>=`) |
| D | 3-ene-2025 | 245 días | Sí |

`churn_% = 2/4 = 50 %` · `retencion_% = 50 %`.

Este ejemplo (el caso del borde de 89 vs 90 días) está cubierto en [`codigo/tests/test_churn.py`](../codigo/tests/test_churn.py).

## El umbral de 90 días no encaja con este negocio

En los datos, los clientes recompran muy espaciado:

| Indicador | Valor |
|---|---|
| Facturas por cliente (media) | 1.86 |
| Clientes con una sola factura | 77 de 172 |
| Mediana de días entre dos compras del mismo cliente | **~669 días** (~22 meses) |
| Recompras que ocurren en menos de 90 días | 10.8 % |
| Recompras en menos de 180 días | 17.6 % |
| Recompras en menos de 365 días | 29.1 % |

Con ese ritmo de compra, un cliente "normal" ya habría sido marcado como abandonado varias veces entre compra y compra. El resultado:

| Umbral | Churn | Retención |
|---|---|---|
| 30 días | 98.26 % | 1.74 % |
| 60 días | 95.35 % | 4.65 % |
| 90 días | 90.70 % | 9.30 % |
| **120 días (panel final)** | **88.95 %** | **11.05 %** |
| 180 días | 83.14 % | 16.86 % |

**Cómo lo abordaría con el negocio:**

1. Preguntar al negocio cuál es el ciclo de recompra esperado (no es lo mismo un cable que una laptop, ni un distribuidor que un consumidor final).
2. Calcular el umbral por **tipo de cliente** y/o **categoría**, por ejemplo con el percentil 75–90 de las brechas entre compras.
3. Ampliar el rango del parámetro (hoy llega a 180 días; aquí tendría sentido llegar a 730).
4. Documentar la definición en el propio reporte, para que nadie lea "91 % de abandono" como un dato absoluto.

## Churn por categoría vs churn de cliente

En una tabla con la categoría en las filas, el contexto de filtro incluye la categoría: un cliente cuenta como "churn" en *Mouse* si no compró *Mouse* en el umbral de días, **aunque siga comprando laptops**. Es una métrica válida ("abandono de la categoría"), pero no debe leerse como "clientes perdidos". En el total de la tabla sí se mide el cliente completo.

## Cómo validar

```bash
python codigo/python/validar_churn.py --por-categoria --sensibilidad 30,60,90,120,180
python codigo/python/ejecutar_sql.py --comparar      # misma lógica en SQL
```
