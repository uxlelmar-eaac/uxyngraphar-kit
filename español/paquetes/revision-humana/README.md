# Revisión humana

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete revision-humana» / «sigue el protocolo revision humana» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/revision-humana`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/recoger-pendientes.md` → `$P/proceso/preparar-revision.md` → `$P/proceso/comprobar-decisiones.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/revision-humana/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-revision.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Recorre los paquetes instalados y reúne las fichas que esperan una decisión de una persona (instrucciones por aprobar, ADR propuestas, mejoras y EVO pendientes, reglas y ajustes propuestos…) en `REVISION.md`; cada paquete declara qué status esperan.

## Lo que decide la persona

- Escribe en la columna «Decisión» de `uxyngraphar/trabajo/revision-humana/REVISION.md` un status de «Opciones», `posponer` o nada, y ejecuta `python3 $P/scripts/revision.py aplicar --humano`. Cada decisión se aplica con el comando propio del paquete (aprobar una instrucción comprueba su alcance).
- `dias_aviso` (14) en `uxyngraphar/trabajo/revision-humana/ajustes.json`: a partir de cuántos días un pendiente se señala como antiguo.
