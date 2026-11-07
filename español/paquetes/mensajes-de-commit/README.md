# Mensajes de commit

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete mensajes-de-commit» / «sigue el protocolo mensajes de commit» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/mensajes-de-commit`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/preparar-commit.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/mensajes-de-commit/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Cada commit lleva un asunto `tipo(ámbito): resumen` en inglés ASCII, en imperativo y de 72 caracteres como máximo, con una sola intención; las ramas, `tipo/descripcion-corta`. `commits.py` lo comprueba antes (`--mensaje`) y después del commit.

## Lo que decide la persona

- Ajustes en `uxyngraphar/trabajo/mensajes-de-commit/ajustes.json`: `commits_revisar` (cuántos commits revisa `commits.py` sin argumentos; 20 por defecto).
- Si el proyecto adopta esta convención o mantiene la suya, y si se reescribe algún commit ya publicado.

El idioma del código está en `idiomas-del-codigo`; el tamaño y los nombres del código, en `calidad-de-codigo`.
