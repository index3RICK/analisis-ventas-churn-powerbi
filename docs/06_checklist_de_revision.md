# 6. Checklist de revisión de un reporte de Power BI

Lista que uso para revisar un reporte antes de entregarlo, o para revisar el de otra persona.

## A. Datos de origen

- [ ] ¿Sé de dónde viene cada tabla y con qué frecuencia se actualiza?
- [ ] Revisé nulos, duplicados, tipos de dato y rangos (`codigo/python/validar_calidad_datos.py` como modelo).
- [ ] Hay una **cifra de control** que cuadra contra otra fuente (finanzas, ERP, el archivo original).
- [ ] Las fechas se interpretan con el formato correcto (día/mes vs mes/día).
- [ ] Los números no están guardados como texto.
- [ ] Hay un solo identificador por entidad (un DNI por cliente, un código por categoría).
- [ ] Revisé caracteres especiales y espacios que rompen relaciones (guiones raros, espacios al final).

## B. Modelo

- [ ] Esquema en estrella: hechos al centro, dimensiones alrededor.
- [ ] Relaciones 1 a muchos, filtro de dimensión → hechos. Evitar muchos a muchos y bidireccionales salvo necesidad justificada.
- [ ] Relaciono por **códigos/claves**, no por nombres.
- [ ] Cada valor de la tabla de hechos existe en su dimensión (si no, aparece "(En blanco)" en los visuales).
- [ ] Tabla de fechas propia, continua y **marcada como tabla de fechas**.
- [ ] Ocultar columnas técnicas (claves) a quien consume el reporte.
- [ ] Medidas en tablas de medidas, con carpetas de visualización si son muchas.

## C. Medidas DAX

- [ ] Nombres consistentes, sin tipografía distinta entre medidas parecidas.
- [ ] Uso de `DIVIDE` en vez de `/`.
- [ ] Nada depende de `TODAY()`/`NOW()` sin un motivo explícito y visible.
- [ ] `SUMX`/iteradores solo donde hace falta calcular fila por fila.
- [ ] Probé cada medida con 1 caso calculado a mano.
- [ ] Probé el **borde** (`>=` vs `>`, primer y último día, división entre cero, periodo sin datos).
- [ ] Probé con filtros (segmentaciones) y sin ellos; los totales cuadran.
- [ ] Un `1 - BLANK()` no se convierte en 100 % sin querer.
- [ ] Cada medida tiene un comentario de **qué responde**, no solo de cómo se calcula.

## D. Visuales

- [ ] Cada visual responde a una pregunta concreta.
- [ ] Los títulos dicen qué mide y en qué unidad.
- [ ] Los porcentajes y variaciones están bien rotulados (¿pp o %? ¿contra qué periodo?).
- [ ] Los colores tienen significado consistente (churn al alza = malo = rojo).
- [ ] Probé el reporte con una selección vacía y con una selección extrema.
- [ ] Las tablas ordenadas indican su orden (una tabla ordenada con muchos ceros parece "incompleta").

## E. Rendimiento

- [ ] Medí con el **Analizador de rendimiento** (View → Performance analyzer).
- [ ] Revisé medidas con `FILTER` anidados o iteradores sobre tablas grandes con **DAX Studio**.
- [ ] Reduje columnas y filas innecesarias en Power Query.
- [ ] Preferí columnas numéricas y claves enteras en las relaciones.

## F. Entrega y mantenimiento

- [ ] Documenté las **definiciones de negocio** (qué es churn, qué es una venta) dentro del reporte.
- [ ] El reporte indica la fecha de última actualización de los datos.
- [ ] Hay un responsable y un calendario de actualización.
- [ ] El `.pbix` y el código DAX están en control de versiones.
- [ ] Quien recibe el tablero sabe qué **no** puede responder.
