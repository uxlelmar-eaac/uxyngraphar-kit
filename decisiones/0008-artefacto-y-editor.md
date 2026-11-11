# 0008 · Artefacto zip reproducible y espacio de nombres por editor

- **Estado:** aceptada
- **Fecha:** 2026-11-11

## Contexto

Para guardar sistemas en un servidor y compartirlos hace falta un formato de intercambio estable y un modo de que dos
autores no choquen con el mismo id.

## Decisión

1. **Artefacto:** `<id>-<version>.zip` con una sola carpeta raíz `<id>/` que contiene la construcción (fuente +
   `scripts/comun/` de `_base` + `INTEGRIDAD.json`). Reproducible: fecha fija 1980-01-01, orden alfabético, permisos
   0644 (0755 para `.py`). Mismo contenido, misma sha256 (`artefacto.py`).
2. **Al recibir un artefacto** (motor y servidor) se rechaza: rutas absolutas, `..`, barras invertidas, enlaces
   simbólicos, nombres no ASCII o con espacios, más de una raíz, cifrado, más de 2000 archivos, más de 50 MB
   descomprimido o compresión sospechosa. Después se valida como sistema construido.
3. **Editor:** cada sistema pertenece a un editor (`editor` en `sistema.json`, por defecto `uxyngraphar`). En el servidor
   la clave es `editor/id`; las versiones publicadas son inmutables (se pueden retirar, no reemplazar).
4. **Campos de distribución opcionales** en `sistema.json`: `editor`, `idioma`, `licencia`
   (SPDX o `propietaria`), `etiquetas` (hasta 12, kebab-case) y `repositorio` (https).

## Consecuencias

- En un proyecto los sistemas siguen instalados por id (`uxyngraphar/sistemas-de-gobernanza/<id>/`): si dos editores
  publican el mismo id, el motor prefiere `uxyngraphar` y pide `editor/id` para el otro; no se pueden instalar los dos
  en el mismo proyecto.
- La licencia y el editor preparan la venta y el reparto de sistemas de terceros, que llegarán con otro ADR.
