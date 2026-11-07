# Cambios

## 1.0.0

- Nace de la división de `calidad-de-codigo` 1.1.0 (que pasa a 2.0.0): se lleva el problema `codigo-en-idioma-mezclado`.
- Trae de `calidad-de-codigo` `scripts/glosario.py`, `plantillas/GLOSARIO.md`, `referencia/idioma.md` y la skill `consultar-glosario`. El glosario del proyecto vive en `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md` (antes en `trabajo/calidad-de-codigo/`) y sigue en «protegidos».
- `scripts/idiomas.py` (verificación) hereda de `calidad.py` el aviso de nombre de archivo no ASCII, con los mismos ajustes `raices`, `extensiones` y `excluir`.
- Límites propios (de la regla de idioma de `calidad-de-codigo`: artefactos en inglés ASCII, i18n, glosario, contratos externos, código antiguo), proceso `diagnosticar` → `escribir-codigo` → `verificar`, skill nueva `revisar-idioma`, ejemplo resuelto y pruebas propias.
- `referencia/idioma.md` deja la tabla «Formato por lenguaje» en `calidad-de-codigo` y el idioma de commits y ramas en `mensajes-de-commit`.
