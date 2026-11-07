# Mapa de módulos

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete mapa-de-modulos» / «sigue el protocolo mapa de modulos» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/mapa-de-modulos`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/identificar-area.md` → `$P/proceso/actualizar-contexto.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/mapa-de-modulos/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-areas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## Dónde vive cada contexto

Un contexto `ARE-…` por área funcional, en una carpeta con el nombre del área: `uxyngraphar/trabajo/mapa-de-modulos/<area>/ARE-<fecha>-<area>.md`. El nombre de la carpeta es el nombre que se cita en `depends_on`. Estados (heredados de 1.x): `active`, `planned` y `deprecated`.

## Lo que decide la persona

- Qué áreas existen y cómo se llaman cuando el código no lo deja claro (partir o fusionar áreas que condicionan el sistema va como ADR en `decisiones-de-arquitectura`).
- `owners` de cada área.
