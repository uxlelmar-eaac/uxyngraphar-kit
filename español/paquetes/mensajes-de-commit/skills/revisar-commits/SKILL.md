---
name: revisar-commits
description: Ejecuta commits.py sobre los últimos commits y separa los que no cumplen en propios y locales (se corrigen) y publicados o ajenos (no se reescriben).
resuelve: [commits-sin-convencion]
---

# Revisar commits

## Cuándo usarla

- Al final de la fase `preparar-commit`, sobre los commits nuevos.
- Cuando la persona pide un diagnóstico del historial reciente al adoptar la convención.

## Pasos

1. Commits nuevos: `python3 $P/scripts/commits.py <n>`. Historial reciente: `python3 $P/scripts/commits.py` (los últimos `commits_revisar`).
2. Cada línea `commit <sha>: «…» no cumple Conventional Commits en inglés ASCII (≤72 caracteres)` es un asunto inválido. La última resume: `mensajes-de-commit: <n> commits revisados, <m> problemas`. Código 0 = sin problemas; 1 = hay problemas.
3. Para cada commit listado, mira si está publicado: `git branch -r --contains <sha>` no vacío = publicado.
4. Propio y local → skill `redactar-commit` y `git commit --amend` (o un rebase interactivo si no es el último, solo sobre commits tuyos). Publicado o de otra persona → no se toca.
5. En un diagnóstico de adopción, no reescribas nada: resume cuántos commits cumplen y los fallos más frecuentes (sin tipo, en otro idioma, demasiado largos) para que la persona decida.

## Resultado

- Ningún commit tuyo y local fuera de la convención; los heredados, a la vista y sin reescribir.
