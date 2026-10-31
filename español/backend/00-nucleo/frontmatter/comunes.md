# Frontmatter — comunes

## Organización por estados y fechas (R-17)

`<seccion>/<estado>/YYYY-MM-DD/<slug>.md`: `01-pendientes` ·
`02-en-progreso` · `03-completadas` · `04-archivadas` · `05-canceladas` ·
`06-listas-para-eliminar`. `YYYY-MM-DD` = fecha de creación; se conserva
al moverse de estado. `status` y carpeta deben coincidir. Nombre de
archivo = slug; el `id` es el identificador global estable.

Detalle: [organizacion-estados-fechas.md](../../10-guias/organizacion-estados-fechas.md).

## Campos comunes

| Campo | Valores | Uso |
|-------|---------|-----|
| `id` | slug estable (`auth-login`, `ADR-001`) | Identificador único |
| `status` | ver ficha del tipo | Estado del documento |
| `areas` | lista de ids de `25-areas/` | Dominios afectados |
| `fecha` | `YYYY-MM-DD` | Creación o última revisión |
| `severidad` | `baja` \| `media` \| `alta` \| `critica` | Auditorías |
