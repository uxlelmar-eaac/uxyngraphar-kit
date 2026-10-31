# Auditorías — índice
<!-- uxyngraphar:inicio -->

Las auditorías e investigaciones formales se organizan por **estado** y, dentro, por **fecha de creación** (`YYYY-MM-DD`). El árbol es el índice; no se mantiene tabla manual.

```
40-auditorias/
├── 01-pendientes/YYYY-MM-DD/   ← pendiente
├── 02-en-progreso/YYYY-MM-DD/  ← activa (en curso)
├── 03-completadas/YYYY-MM-DD/  ← cerrada
├── 04-archivadas/YYYY-MM-DD/   ← archivada
├── 05-canceladas/YYYY-MM-DD/   ← cancelada
└── 06-listas-para-eliminar/    ← para-eliminar
```

- En curso: `02-en-progreso/`
- Vista viva de promociones pendientes: `python3 docs/scripts/decisiones/decisiones.py scan`
- Ver [_PROTOCOLO.md](_PROTOCOLO.md) · [_PLANTILLA.md](_PLANTILLA.md)

(En Windows: `py -3` en lugar de `python3`.)

Estados (`status`): `pendiente` (01) | `activa` (02) | `cerrada` (03) | `archivada` (04) | `cancelada` (05). Severidad: `baja` | `media` | `alta` | `critica`.
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
