# Manuales operativos

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete manuales-operativos» / «sigue el protocolo manuales operativos» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/manuales-operativos`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/localizar-manual.md` → `$P/proceso/redactar-pasos.md` → `$P/proceso/entregar-para-verificacion.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/manuales-operativos/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## Dónde vive cada manual

Un manual `MAN-…` por procedimiento en `uxyngraphar/trabajo/manuales-operativos/` (se pueden agrupar en subcarpetas con `--en despliegue`, `--en incidentes`…). Estados: `borrador` (lo deja el agente), `vigente` (probado por una persona) y `obsoleto` (heredado de 1.x: el procedimiento ya no aplica).

## Lo que decide la persona

- Pasar un manual a `vigente` tras ejecutarlo: `python3 $P/scripts/comun/fichas.py estado MAN-… vigente --humano`, y anotar la fecha en `ultima_verificacion`.
- De dónde se obtiene cada variable sensible (gestor de secretos, panel del proveedor): el manual solo la nombra.
