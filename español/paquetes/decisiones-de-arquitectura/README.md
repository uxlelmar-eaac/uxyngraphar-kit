# Decisiones de arquitectura

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete decisiones-de-arquitectura» / «sigue el protocolo decisiones de arquitectura» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/decisiones-de-arquitectura`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/consultar-vigentes.md` → `$P/proceso/redactar-adr.md` → `$P/proceso/someter-a-evaluacion.md` → `$P/proceso/registrar-reemplazo.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/decisiones-de-arquitectura/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

El agente consulta las ADR vigentes antes de decidir algo estructural, redacta una ADR nueva (o un reemplazo) con opciones reales y la deja `en-evaluacion`; la persona la acepta o la rechaza.

## Lo que decide la persona

- Aceptar o rechazar una ADR: `python3 $P/scripts/comun/fichas.py estado <ADR-…> aceptada --humano` (o `rechazada`). Una aceptada es vinculante hasta que otra la reemplace.
- Si una decisión necesita una ADR: el agente lo propone; la persona puede pedirla aunque el agente no lo vea necesario.
