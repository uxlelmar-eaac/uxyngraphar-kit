# Deuda y mejoras

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete deuda-y-mejoras» / «sigue el protocolo deuda y mejoras» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/deuda-y-mejoras`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/clasificar-hallazgo.md` → `$P/proceso/buscar-duplicados.md` → `$P/proceso/registrar.md` → `$P/proceso/implementar-aprobada.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/deuda-y-mejoras/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Lo que se ve mal durante una tarea y no forma parte del pedido se anota como ficha `MEJ-…` con evidencia, sin arreglarlo; una persona decide qué se aprueba y solo entonces se implementa.

## Lo que decide la persona

- Aprobar o rechazar una mejora: `python3 $P/scripts/comun/fichas.py estado MEJ-… approved --humano` (o `rejected`).
- La prioridad final de la cola (`ahora`, `pronto`, `despues`); el agente solo la propone.
- Ajustes en `uxyngraphar/trabajo/deuda-y-mejoras/ajustes.json`: `max_por_tarea` (3 fichas nuevas por tarea como máximo).
