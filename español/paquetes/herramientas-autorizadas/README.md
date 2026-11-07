# Herramientas autorizadas

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete herramientas-autorizadas» / «sigue el protocolo herramientas autorizadas» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/herramientas-autorizadas`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/buscar-herramienta.md` → `$P/proceso/ejecutar-herramienta.md` → `$P/proceso/proponer-herramienta.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/herramientas-autorizadas/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-herramientas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Si una herramienta autorizada y vigente cubre el pedido entero, se ejecuta tal como dice su ficha leyendo solo su ficha y sus anclas; si no, el pedido sigue el proceso normal y, si el procedimiento se repite, el agente lo propone.

## Lo que decide la persona

- Autorizar: `python3 $P/scripts/comun/fichas.py nueva autorizada --slug <slug> --humano`, rellenando `authorized_by`, el alcance, los riesgos y las anclas (si viene de una propuesta, se copia de ella). Después, la propuesta: `fichas.py estado <PRO-…> promovida --humano`.
- Rechazar una propuesta: `fichas.py estado <PRO-…> rejected --humano`.
- Revocar una herramienta: `fichas.py estado <HER-…> revoked --humano`.
