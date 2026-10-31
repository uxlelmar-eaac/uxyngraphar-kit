# Matriz de cobertura — proyectos (documento vivo)

Mapa de **qué cubre el pack** para proyectos en general. Actualizar al adoptar, al cerrar fichas `EVO-*` aprobadas o en revisión trimestral.

Leyenda: **C** cubierto · **P** parcial · **F** falta · **EVO** ficha en [`46-evolucion-documentacion/`](INDICE.md)

| Dimensión | Servidor/API | Cliente/UI | Multi-repo | Espejo 50 | IA / instrucciones | Ops 30 | Revisión de pendientes | Estado | Ficha EVO |
|-----------|--------------|------------|------------|-----------|-------------------|--------|-------------------|--------|-----------|
| Adopción inicial pack | C | C | P | C | C | P | C | — | — |
| Instrucción approve-before-execute | C | C | C | C | C | — | — | — | — |
| Organización por estados y fechas (R-17) | C | C | C | — | C | C | C | 1.0.0 | EVO-20260823-estados-fechas |
| Alcance de 46 — solo sistema documental (R-18) | C | C | C | — | C | C | C | 1.0.0 | EVO-20260823-estados-fechas |
| Fichas HTTP / BFF | C | P | C | C | C | — | — | — | — |
| Deuda producto (45) | C | C | C | — | C | — | C | — | — |
| Evolución pack (46) | C | C | P | — | C | — | C | — | — |
| Ciclo vinculante actos | C | C | P | C | C | P | C | — | — |
| Auditorías + promoción | C | C | P | C | C | — | C | — | — |
| Monorepo docs fusionados | P | P | P | P | P | — | — | plantilla | — |
| Validación scripts / CI | C | C | — | — | — | — | C | — | — |
| Secretos / placeholders | C | C | C | — | C | C | — | — | — |
| Detección deriva espejo vs código | F | F | — | F | — | — | — | 1.0.0 | EVO-20260823-deriva-espejo |
| Andamiaje de instrucciones (CLI) | F | F | — | — | F | — | — | 1.0.0 | EVO-20260823-cli-andamiaje |
| Validador unificado (Python) | F | F | — | — | — | — | F | 1.0.0 | EVO-20260823-validador-python |
| Métricas del sistema documental | F | F | — | — | F | — | F | 1.0.0 | EVO-20260823-metricas |
| Actualización de packs adoptados | F | F | F | — | — | — | — | 1.0.0 | EVO-20260823-actualizador-pack |
| Archivado periódico automático | F | F | — | — | — | — | F | 1.0.0 | EVO-20260823-archivado-periodico |
| Ganchos git del ciclo vinculante | F | F | — | — | F | — | — | 1.0.0 | EVO-20260823-ganchos-git |
| Ahorro de tokens y herramientas de contexto | F | F | F | — | F | — | F | 1.0.0 | EVO-20261015-ahorro-tokens-herramientas |
| Ampliación del alcance de código (R-21) | C | C | C | — | C | — | C | 1.0.0 | EVO-20261026-ampliacion-alcance |
| Idioma del código del producto (R-22) | C | C | P | — | C | — | — | 1.0.0 | EVO-20261028-politica-idioma |
| Nombres autoexplicativos (R-23) | C | C | — | — | C | — | — | 1.0.0 | EVO-20261029-nombres-autoexplicativos |

## Cómo usar

1. Tras adopción: marcar **P** o **F** en filas relevantes al repo real.
2. Si **F** o mejora general del sistema documental: crear ficha desde [_PLANTILLA-cobertura.md](_PLANTILLA-cobertura.md) en `01-pendientes/YYYY-MM-DD/` (R-17, R-18).
3. Al aprobar EVO: cambiar columna Estado, enlazar id en **Ficha EVO** y mover la ficha a `02-en-progreso/` → `03-completadas/`.
4. No usar esta matriz para bugs de producto → `45-mejoras-propuestas/`.

Ver [_PROTOCOLO.md](_PROTOCOLO.md).
