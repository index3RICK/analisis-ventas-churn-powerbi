# Archivo de Power BI

| Archivo | Descripción |
|---|---|
| `analisis_ventas_churn.pbix` | Reporte con los cuatro paneles (Power BI Desktop, solo Windows) |

## Cómo abrirlo

1. Abre el `.pbix` con Power BI Desktop.
2. Si pide la ruta del origen: **Transformar datos > Configuración de origen de datos** y apunta a `datos/ventas_tecnologia_barcelona.csv`.
3. Si ves importes 100 veces mayores, revisa la configuración regional de `Precio` y `Total` (ver [`codigo/powerquery/Analisis_Ventas.m`](../codigo/powerquery/Analisis_Ventas.m)).

## Cifras para comprobar que todo cargó bien

- `ventas_totales` = 2.082.843,02 sin filtros, igual que la tarjeta de facturación del panel 1.
- `Fecha_Ref` = 05/09/2025 (no depende de `TODAY()`).
- Con umbral 120: churn 88,95 %, retención 11,05 % y churn del año anterior 92,50 %.
- Panel 4: 19 / 5 / 24 / 27 / 97 clientes por segmento (suman 172) y CPA máximo ≈ $1,38 mil.
