# 0004 · Status de las fichas en español

- **Estado:** aceptada
- **Fecha:** 2026-11-10

## Contexto

Mezclar status en inglés (`pending`, `approved`, `done`) con sinónimos en español produce duplicados y búsquedas que no encuentran nada, y las personas que deciden leen y escriben esos status a mano.

## Decisión

Los status siguen el vocabulario de [`NOMENCLATURA.md`](../español/motor/NOMENCLATURA.md) §4: español, kebab-case y con concordancia de género con el tipo de ficha. Las excepciones de dominio se declaran en `nomenclatura.json` y solo se amplían con una decisión de la persona. Las fichas de un proyecto con status en otro vocabulario se pasan con `uxyngraphar nomenclatura migrar` según `vocabulario.json`.

## Consecuencias

- Ningún sistema del catálogo usa status heredados (`validar` da 0 avisos).
- Los campos heredados del frontmatter en inglés (`approved_at`…) se mantienen por compatibilidad; los nuevos van en español.
