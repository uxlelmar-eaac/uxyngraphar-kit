---
id: AUD-YYYYMMDD-slug
status: activa
investigator: ai
severidad: media
fecha: YYYY-MM-DD
areas: [ejemplo]
modules: []
endpoints: []
questions: []
findings_count: 0
espejo_actualizar: []       # paths espejo a sync al promover hallazgos
promociones: []             # [{ tipo, destino, notas }] — tipo: canon|adr|ficha|espejo
related_instrucciones: []
---

<!-- Ubicación (R-17): 40-auditorias/02-en-progreso/YYYY-MM-DD/AUD-YYYYMMDD-slug.md.
     Cerrada → 03-completadas/; cancelada → 05-canceladas/; histórica → 04-archivadas/. -->

# AUD-YYYYMMDD — Título

## Preguntas

1. …

## Método

Qué se leyó / reprodujo (archivos, logs).

## Hallazgos

1. **Título** — evidencia (path:línea) — impacto

## Recomendaciones

- Inmediato / después / no hacer

## Promociones propuestas

Registrar en frontmatter `promociones`:

| tipo | destino | notas |
|------|---------|-------|
| `canon` | `00-nucleo/...` o CONTEXTO | Actualizar regla canon |
| `adr` | `20-decisiones/ADR-NNN-slug.md` | Nueva ADR |
| `ficha` | `15-rutas/...` | Ficha endpoint/BFF |
| `espejo` | `50-sistema-integral/...` | Sync espejo |

Paths espejo pendientes → `espejo_actualizar` en frontmatter.

Ver [sync-documentacion-pr.md](../10-guias/sync-documentacion-pr.md) sección Promoción desde auditoría.

## Decisiones a tomar (promociones)

Registrar una tarjeta por promoción pendiente. Sustituir el slug por el id real y `N` por índice.

<!-- decision-group: AUD-YYYYMMDD-slug-promo-1 -->
- [ ] <!-- decision:aprobar --> **Promover** — tipo `canon|adr|ficha|espejo` según tabla arriba
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar**

## Cierre

Fecha, `status: cerrada`, mover a `03-completadas/YYYY-MM-DD/`, qué se implementó (enlaces a instrucciones/commits).
