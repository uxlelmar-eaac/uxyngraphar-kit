# Frontmatter — mejora (`45-mejoras-propuestas/`)

Ruta: `45-mejoras-propuestas/<estado>/YYYY-MM-DD/MEJ-YYYYMMDD-slug.md`.
Estados: `01` (`pending`) · `02` (`approved`) · `03` (`done`) · `04`
(`archivada`) · `05` (`rejected`) · `06` (`para-eliminar`).

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|-------|
| `id` | string | sí | `MEJ-YYYYMMDD-slug` |
| `status` | enum | sí | `pending` \| `approved` \| `rejected` \| `done` \| `archivada` \| `para-eliminar` |
| `tipo` | enum | sí | `deuda-tecnica` \| `refactor` \| `diseno` \| `tests` \| `docs` \| `perf` \| `seguridad` \| `bug` |
| `severidad` | enum | sí | `baja` \| `media` \| `alta` |
| `prioridad` | enum | no | `ahora` \| `despues` \| `algun-dia` |
| `related_instruction` | string | sí | Instrucción donde se detectó |
| `instruction_derivada` | string | no | Tras aprobación humana |
| `evidencia` | string[] | sí | `path:línea` |
