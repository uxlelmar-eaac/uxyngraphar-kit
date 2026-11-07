# Mensajes de commit

Mantiene el historial de git legible y estable: cada commit con un asunto en Conventional Commits, en inglés ASCII, en imperativo, de una sola intención y de 72 caracteres como máximo. `commits.py` lo comprueba sin IA, sobre un mensaje antes de hacer el commit o sobre los últimos commits.

## Qué resuelve

Sin una convención, cada persona y cada agente escriben el mensaje a su manera («cambios», «añadir cupones», «WIP fix 2») y el historial deja de servir para saber qué cambió y por qué, para generar notas de versión o para revertir un cambio concreto. Este paquete fija el formato del asunto, una intención por commit, el nombre de las ramas y qué commits se pueden corregir (solo los locales y propios).

## Problemas que cubre

- `commits-sin-convencion`: mensajes de commit fuera de Conventional Commits en inglés ASCII o de más de 72 caracteres.

## Fuera de alcance

- Idioma del código, de los comentarios y de los títulos de PR: `idiomas-del-codigo`.
- Tamaño de los archivos y nombres de identificadores del cambio: `calidad-de-codigo`.
- Notas de versión y CHANGELOG del producto generados a partir de los commits: no lo cubre el kit.
- Ganchos de git, commitlint y reglas de protección de ramas en el servidor: no lo cubre el kit; son herramientas del proyecto (este paquete no las instala).

## Cuándo usarlo

- Cuando el pedido incluye hacer o proponer commits, o crear una rama.
- Cuando `commits.py` informa de un commit propio que aún no se publicó.
- Al adoptar la convención en un proyecto existente (diagnóstico del historial reciente con `commits.py`).

## Cuándo no usarlo

- Para reescribir commits ya publicados o de otras personas: no se reescriben.
- En proyectos que ya fijan otra convención de commits (commitlint propio, otro formato): manda la del proyecto; la persona decide si adoptar esta.

## Entradas y salidas

- Entradas: el cambio a entregar, el historial de git (`git log`) y el ajuste `commits_revisar` en `uxyngraphar/trabajo/mensajes-de-commit/ajustes.json`.
- Salidas: commits con asunto válido, ramas `tipo/descripcion-corta` y el informe de `commits.py` (`commit <sha>: motivo` y un resumen con el número de problemas).

## Paquetes complementarios

- `idiomas-del-codigo`: el código del cambio en inglés ASCII, como el mensaje que lo describe.
- `calidad-de-codigo`: el cambio que se entrega, dividido y nombrado antes del commit.
