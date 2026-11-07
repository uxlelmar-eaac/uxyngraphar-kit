# Notas de memoria

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete notas-de-memoria» / «sigue el protocolo notas de memoria» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/notas-de-memoria`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/buscar-en-memoria.md` → `$P/proceso/guardar-nota.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/notas-de-memoria/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## Dónde viven las notas

`uxyngraphar/trabajo/notas-de-memoria/memoria/`: notas `MEM-…` (`vigente` o `archivada`). El agente las escribe cuando la persona quiere conservar algo y solo las lee si el pedido lo pide expresamente (`python3 $P/scripts/notas.py buscar <texto>`).

## Lo que decide la persona

- Qué merece una nota y hasta cuándo vale.
- Si una nota que contradice el pedido sigue vigente.
- Retirar documentos enteros: eso es `documentos-archivados`.
