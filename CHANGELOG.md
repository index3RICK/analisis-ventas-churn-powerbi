# Historial de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [1.0.0] — 2026-11-20

Proyecto terminado: cuatro paneles verificados.

### Agregado
- **Panel 4 de reactivación:** segmentos, rankings (rápido y por valor), KPI de ROI y CPA máximo (`codigo/dax/Medidas_Reactivacion/`).
- Un archivo `.dax` por medida (63) con comentarios en español, y un README por panel en `paneles/`.
- `codigo/powerquery/Analisis_Ventas.m` con la limpieza de datos.
- Datos de origen en `datos/` (CSV) e `img/` con las capturas.
- Opciones `--iva` y `--corregir-agencias` en los scripts de Python.
- Lecciones 9 a 14 en `docs/05_lecciones_aprendidas.md`.

### Corregido
- **Importes ×100** por configuración regional en Power Query (`Precio` y `Total` con `en-US`).
- **IVA** adaptado al 15 % (Ecuador); la columna `Total` del archivo deja de usarse.
- Agencia `Tech DCM Barcelona` unificada con `Tech BCN Norte`.
- Ranking de valor de reactivación (`1, 1, 1...`).
- Clientes convertidos esperados y CPA con la misma población.
- Segmentos: `Dormido reciente` alcanzable; textos del segmentador idénticos; fila de total.
- Medidas del año anterior con la última compra "a la fecha" del corte PY (92.50 %, 160 clientes).
- Flechas "vs PY" en puntos porcentuales; `BLANK()` en periodos sin ventas.

### Cambiado
- Estructura del repositorio: `codigo/`, `datos/`, `img/`, `paneles/`.

## [0.1.0] — 2026-10-27

### Agregado
- Estructura inicial del repositorio y documentación en español.
- DAX organizado por tema, con comentarios.
- Scripts de validación en Python (`validar_calidad_datos.py`, `validar_churn.py`, `ejecutar_sql.py`).
- Consulta SQL equivalente del churn por categoría.
- Pruebas automáticas de la lógica de churn.

### Corregido
- `Fecha_Ref` ya no depende de `TODAY()`: se ancla a la última venta.
- `DIM_Calendario` termina en el último año con ventas.
