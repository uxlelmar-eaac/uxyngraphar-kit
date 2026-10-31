# Frontmatter — auditoría (`40-auditorias/`)

Ruta: `40-auditorias/<estado>/YYYY-MM-DD/AUD-YYYYMMDD-slug.md`. Estados:
`01` (`pendiente`) · `02` (`activa`) · `03` (`cerrada`) · `04`
(`archivada`) · `05` (`cancelada`) · `06` (`para-eliminar`).

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|-------|
| `id` | string | sí | `AUD-YYYYMMDD-slug` |
| `status` | enum | sí | `pendiente` \| `activa` \| `cerrada` \| `archivada` \| `cancelada` |
| `areas` | string[] | sí | |
| `severidad` | enum | sí | |
| `espejo_actualizar` | string[] | no | Paths espejo a sync al promover |
| `promociones` | object[] | no | `{ tipo, destino, notas }`. Tipos: `canon` \| `adr` \| `ficha` \| `espejo` |

Al revisar pendientes (`decisiones-pendientes`): `aprobar` (promover) → `status: cerrada` y `03-completadas/`; `rechazar` → `status: cancelada` y `05-canceladas/`.
