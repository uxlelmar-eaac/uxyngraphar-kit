# Cambios

## 1.0.0

- Nace de la división de `calidad-de-codigo` 1.1.0 (que pasa a 2.0.0): se lleva el problema `commits-sin-convencion`.
- Trae de `calidad-de-codigo` la fase `preparar-commit`, la skill `redactar-commit`, el límite de commits y la revisión de commits de `calidad.py --commits [N]`, que pasa a `scripts/commits.py [N]` con el mismo ajuste `commits_revisar` (20) y el mismo mensaje por problema.
- `commits.py --mensaje "…"` comprueba un asunto antes de hacer el commit.
- El máximo de 72 caracteres se aplica al asunto completo, como dice el límite; `calidad.py` solo limitaba el resumen tras `tipo(ámbito): ` (71 caracteres).
- El nombre de las ramas (`tipo/descripcion-corta`), que estaba en `referencia/idioma.md` y en la fase `preparar-commit`, pasa a ser el límite 4.
- Límites propios (formato, resumen, una intención por commit, ramas, solo se corrige lo local y propio), skill nueva `revisar-commits`, `referencia/commits.md` con los tipos y su uso, ejemplo resuelto y pruebas propias.
