# Frontmatter — ADR (`20-decisiones/`)

Ruta: `20-decisiones/<estado>/YYYY-MM-DD/ADR-NNN-kebab-slug.md`. Estados:
`01` (`propuesta`) · `03` (`aceptada`) · `04` (`reemplazada`, `obsoleta`) ·
`05` (`rechazada`) · `06` (`para-eliminar`).

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|-------|
| `id` | string | sí | `ADR-NNN` |
| `status` | enum | sí | `propuesta` \| `aceptada` \| `reemplazada` \| `obsoleta` \| `rechazada` |
| `areas` | string[] | sí | |
| `fecha` | string | sí | |
