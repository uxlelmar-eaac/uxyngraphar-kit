# Reglas del proyecto

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete reglas-del-proyecto» / «sigue el protocolo reglas del proyecto» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/reglas-del-proyecto`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/consultar-reglas.md` → `$P/proceso/implementar.md` → `$P/proceso/verificar.md` → `$P/proceso/proponer-cambios.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/reglas-del-proyecto/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-reglas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Las convenciones del equipo se escriben como reglas (`REG-*`, comprobables con expresiones regulares), cada incumplimiento justificado pasa por una excepción (`EXC-*`) que aprueba una persona. Los ajustes locales que adaptan otros paquetes a este proyecto están en `adaptaciones-de-paquetes`.

## Lo que decide la persona

- Activar o retirar una regla: `python3 $P/scripts/comun/fichas.py estado REG-… activa --humano` (o `retirada`).
- Aprobar o rechazar una excepción: `python3 $P/scripts/comun/fichas.py estado EXC-… aprobada --humano` (o `rechazada`), y escribir `aprobada_por`.
- Ajustes en `uxyngraphar/trabajo/reglas-del-proyecto/ajustes.json`: `raices`, `excluir` y `max_kb` (tamaño máximo de archivo que se comprueba).
