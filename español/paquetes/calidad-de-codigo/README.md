# Calidad de código

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete calidad-de-codigo» / «sigue el protocolo calidad de codigo» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/calidad-de-codigo`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/diagnosticar.md` → `$P/proceso/escribir-codigo.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/calidad-de-codigo/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/calidad.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Todo archivo de código que se escribe cabe en `limite_lineas` (350), se divide por responsabilidad con nombre relacional cuando crece y se nombra por lo que hace; `calidad.py` comprueba el tamaño y los nombres de archivo sin IA.

## Lo que decide la persona

- Ajustes en `uxyngraphar/trabajo/calidad-de-codigo/ajustes.json`: `raices`, `extensiones`, `excluir`, `limite_lineas` y `exenciones_lineas`.
- Las exenciones al límite de líneas y el renombrado de nombres genéricos heredados.

El idioma del código y el glosario están en `idiomas-del-codigo`; el formato de los commits, en `mensajes-de-commit`.
