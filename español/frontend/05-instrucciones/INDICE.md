# Instrucciones — índice
<!-- uxyngraphar:inicio -->

Las instrucciones se organizan por **estado** y, dentro, por **fecha de creación** (`YYYY-MM-DD`). El árbol de carpetas es el índice; no se mantiene tabla manual de fichas.

```
05-instrucciones/
├── 01-pendientes/YYYY-MM-DD/   ← draft, awaiting_approval
├── 02-en-progreso/YYYY-MM-DD/  ← approved, executing
├── 03-completadas/YYYY-MM-DD/  ← done
├── 04-archivadas/YYYY-MM-DD/   ← archivada
├── 05-canceladas/YYYY-MM-DD/   ← cancelled
└── 06-listas-para-eliminar/    ← para-eliminar
```

## Plantillas (raíz, fuera de estados)

| Plantilla | `acto` |
|-----------|--------|
| [_PLANTILLA.md](_PLANTILLA.md) | `crear` / `editar` / `corregir` |
| [_PLANTILLA-solo-documentacion.md](_PLANTILLA-solo-documentacion.md) | `mejorar-docs` |
| [_PLANTILLA-generar-espejo-integral.md](_PLANTILLA-generar-espejo-integral.md) | `crear` |
| [_PLANTILLA-politica-espejo-incremental.md](_PLANTILLA-politica-espejo-incremental.md) | `adoptar` |
| [_PLANTILLA-consolidar-espejo-integral.md](_PLANTILLA-consolidar-espejo-integral.md) | `mejorar-docs` |
| [_PLANTILLA-adopcion-inicial-pack.md](_PLANTILLA-adopcion-inicial-pack.md) | `adoptar` |

## Vista viva de pendientes

`python3 docs/scripts/decisiones/decisiones.py scan` — lista instrucciones `awaiting_approval` y fichas pendientes de todo el pack.

(En Windows: `py -3` en lugar de `python3`.)

Reglas: [_PROTOCOLO.md](_PROTOCOLO.md) · [organizacion-estados-fechas.md](../10-guias/organizacion-estados-fechas.md).

Estados (`status` frontmatter): `draft` | `awaiting_approval` (01) · `approved` | `executing` (02) · `done` (03) · `archivada` (04) · `cancelled` (05) · `para-eliminar` (06).
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
