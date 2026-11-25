# 1. Contexto y objetivos

## Situación

EuroComplice S.L., una empresa de tecnología con tres agencias en Barcelona, vende 50 categorías de producto (laptops, tarjetas de video, smartphones, redes, accesorios...) a tres tipos de cliente: consumidor final, tienda online (Ecommerce) y distribuidores. La dirección quiere un tablero que responda tres preguntas.

## Preguntas de negocio

| # | Pregunta | Dónde se responde |
|---|---|---|
| 1 | ¿Cuánto vendemos, con qué descuento e IVA, y cómo evoluciona? | Panel de ventas (`codigo/dax/Medidas_base_facturacion/`, `Medidas_Inteligencia_Tiempo/`) |
| 2 | ¿Quiénes son los clientes y vendedores que más aportan? | Participación y Pareto (`codigo/dax/Medidas_participacion_ranking/`) |
| 3 | ¿Qué clientes dejaron de comprar y cómo se compara con el año pasado? | Panel "Abandono de clientes" (`codigo/dax/Medidas_churn/`, `Medidas_Rate/`, `Medidas_Serie/`) |

## Alcance de este repositorio

**Incluye:** medidas DAX, validación independiente (Python/SQL), documentación de decisiones y errores.
**No incluye:** el diseño visual del tablero (ver capturas en `img/paneles/`) ni conexión a una base de datos real.

## Cómo se organizó el trabajo

1. Revisar la calidad de los datos de origen (`codigo/python/validar_calidad_datos.py`).
2. Construir el modelo en estrella y las dimensiones.
3. Escribir las medidas de facturación, primero, porque todo lo demás depende de ellas.
4. Construir churn/RFM y la comparación contra el año anterior.
5. **Validar** cada cifra clave por un camino independiente (pandas y SQL).
6. Documentar los errores encontrados y las decisiones.

## Principio de trabajo

> Un número de un tablero no vale nada hasta que alguien lo reconcilió contra otra fuente.

Por eso el repositorio incluye cifras de control (por ejemplo, la suma de ventas con IVA del 15 % = 2.082.843,02) y scripts que las recalculan.
