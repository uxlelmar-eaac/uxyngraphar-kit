# Instrucciones aprobadas

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete instrucciones-aprobadas» / «sigue el protocolo instrucciones aprobadas» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/instrucciones-aprobadas`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/redactar-instruccion.md` → `$P/proceso/esperar-aprobacion.md` → `$P/proceso/cargar-contexto.md` → `$P/proceso/implementar.md` → `$P/proceso/cerrar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/instrucciones-aprobadas/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-ciclo.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Pedido → instrucción con alcance y anclas → aprobación de una persona → contexto mínimo → cambio solo en las anclas → cierre con `ESTADO.md` al día.

## Lo que decide la persona

- Aprobar una instrucción: `python3 $P/scripts/ciclo.py aprobar <id> --humano` (comprueba el alcance antes de aprobar). Cancelarla: `python3 $P/scripts/comun/fichas.py estado <id> cancelled`.
- El presupuesto en `uxyngraphar/trabajo/instrucciones-aprobadas/ajustes.json`: `max_archivos_codigo` (5), `max_docs` (8), `ampliacion_factor_max` (2.0) y `max_tokens_contexto` (12000).
- Las «Notas» de `ESTADO.md`, debajo del bloque generado.

Las preguntas previas a la instrucción son del paquete `preguntas-de-clarificacion`; si está instalado, la instrucción cita su ficha en `preguntas_id`. Sin él, el ciclo funciona igual.
