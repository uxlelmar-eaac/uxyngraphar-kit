# Límites

Se cumplen en cada commit y rama que el agente crea o propone. Solo una persona puede cambiar los ajustes.

1. **Formato.** El asunto sigue Conventional Commits: `tipo(ámbito): resumen`, con `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` o `revert`; ámbito opcional en minúsculas; `!` tras el ámbito marca un cambio incompatible.
2. **Resumen.** En inglés, ASCII, en imperativo y sin punto final; el asunto completo, de 72 caracteres como máximo. El cuerpo, si lo hay, también en inglés y separado por una línea en blanco.
3. **Una intención por commit.** Un tipo por commit: un arreglo y una función nueva son dos commits.
4. **Ramas.** `tipo/descripcion-corta` en inglés ASCII y kebab-case (`feat/checkout-coupons`).
5. **Solo se corrige lo local y propio.** `git commit --amend` o un rebase solo sobre commits del agente que aún no se publicaron; los commits publicados o de otras personas no se reescriben.
6. **No se debilita la revisión.** El agente no edita `ajustes.json` para que `commits.py` pase.

## Cuándo detenerse y preguntar

- Corregir un mensaje exige reescribir commits ya publicados o de otra persona.
- El proyecto ya tiene otra convención de commits (commitlint, plantilla de mensaje, otro formato): la persona decide cuál manda.
- El cambio mezcla intenciones que no se pueden separar en commits independientes sin romper la compilación o las pruebas.
