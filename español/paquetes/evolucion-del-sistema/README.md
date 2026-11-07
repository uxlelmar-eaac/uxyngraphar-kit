# Evolución del sistema

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete evolucion-del-sistema» / «sigue el protocolo evolucion del sistema» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/evolucion-del-sistema`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/detectar-carencia.md` → `$P/proceso/registrar-evo.md` → `$P/proceso/revisar-cobertura.md` → `$P/proceso/llevar-al-catalogo.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/evolucion-del-sistema/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-evolucion.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Los paquetes son inmutables: este es el canal para mejorarlos. Una EVO describe lo que le falta **al sistema** (un paquete, una plantilla, un proceso), nunca al producto, y llega al catálogo solo cuando una persona la aprueba y la exporta.

## Lo que decide la persona

- Aprobar, rechazar o dar por hecha una EVO: `python3 $P/scripts/comun/fichas.py estado EVO-… approved --humano` (o `rejected`, `done` cuando se publica la versión del paquete que la incorpora).
- Exportarla para llevarla al catálogo: `python3 $P/scripts/evolucion.py exportar --humano [--todas]` (informe en `uxyngraphar/trabajo/evolucion-del-sistema/exportaciones/`); a quién se envía lo decide ella.
- Si urge en este proyecto: un ajuste local en `adaptaciones-de-paquetes` que cite la EVO.
- El contenido de `MATRIZ-COBERTURA.md`.
- Ajustes en `uxyngraphar/trabajo/evolucion-del-sistema/ajustes.json`: `max_por_tarea` (2) y `tipos` (`cobertura`, `proceso`, `plantilla`, `paquete-nuevo`, `herramienta`).
