# Auditorías técnicas

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete auditorias-tecnicas» / «sigue el protocolo auditorias tecnicas» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/auditorias-tecnicas`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/abrir-auditoria.md` → `$P/proceso/investigar.md` → `$P/proceso/concluir.md` → `$P/proceso/promover.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/auditorias-tecnicas/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-auditorias.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Una auditoría (ficha `AUD-…`) responde preguntas concretas sobre el sistema dentro de un alcance fijado, con hallazgos que citan su evidencia y su severidad; no cambia nada: lo que haya que hacer sale como promociones que decide una persona.

## Lo que decide la persona

- Qué promociones propuestas se aceptan (ADR, instrucción, mejora o documentación) y en qué paquete se registran.
- Posponer (`pendiente`), cancelar o mandar a `para-eliminar` una auditoría.
- Ajustes en `uxyngraphar/trabajo/auditorias-tecnicas/ajustes.json`: `severidades` (`critica`, `alta`, `media`, `baja`, `info`), `max_activas` (5) y `dias_sin_cambios` (14).
