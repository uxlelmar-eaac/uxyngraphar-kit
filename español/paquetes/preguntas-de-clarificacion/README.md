# Preguntas de clarificación

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete preguntas-de-clarificacion» / «sigue el protocolo preguntas de clarificacion» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/preguntas-de-clarificacion`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/preguntar.md` → `$P/proceso/cerrar-pregunta.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/preguntas-de-clarificacion/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-preguntas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Pedido → lo que cambia el resultado, en pocas preguntas con opciones → respuestas de la persona en una ficha `PRE-…` → síntesis entregada al trabajo siguiente → pregunta enlazada y cerrada.

## Lo que decide la persona

- Las respuestas: la columna «Elegida» solo recoge lo que ella contesta.
- Los ajustes en `uxyngraphar/trabajo/preguntas-de-clarificacion/ajustes.json`: `preguntas` (`true`) y `dias_en_curso` (7).
- Saltarse las preguntas en un pedido concreto: decir «salta preguntas».

Con `instrucciones-aprobadas` instalado, la síntesis va a «Clarificación» de la instrucción y ambas fichas se citan (`preguntas_id` ↔ `instruccion_id`). Sin él, el paquete funciona igual y la síntesis se entrega en el chat.
