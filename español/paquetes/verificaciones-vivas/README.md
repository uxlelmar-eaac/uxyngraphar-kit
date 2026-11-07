# Verificaciones vivas

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete verificaciones-vivas» / «sigue el protocolo verificaciones vivas» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/verificaciones-vivas`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/acotar-revision.md` → `$P/proceso/ejecutar-revisiones.md` → `$P/proceso/informar.md` → `$P/proceso/derivar-hallazgos.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/verificaciones-vivas/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Bajo pedido, `vivas.py` contrasta lo que documentan los demás paquetes instalados con el código real (rutas, páginas, anclas, decisiones, manuales, ids citados y pruebas de humo) y deja los hallazgos en una tabla con evidencia; no corrige nada.

## Lo que decide la persona

- Cuándo se ejecuta: no es puerta de commit ni de CI.
- Ajustes en `uxyngraphar/trabajo/verificaciones-vivas/ajustes.json`: `raices`, `excluir`, `extensiones`, `prefijo_global` (p. ej. `api` si el servidor lo añade a todas las rutas), `campos_ancla`, `dias_manual` y `humo` (`[{"nombre": "…", "comando": "…", "segundos": 300}]`).
- Si se ejecutan las pruebas de humo (`--ejecutar`) y contra qué entorno.
- Qué hallazgos se corrigen, por qué flujo y cuándo.
