# Mejoras propuestas — índice (cliente)
<!-- uxyngraphar:inicio -->

Deuda técnica, refactors y **bugs** detectados por IA **pendientes de decisión humana**. **No implementar** desde aquí. Organización por estado y fecha (R-17):

```
45-mejoras-propuestas/
├── 01-pendientes/YYYY-MM-DD/   ← pending
├── 02-en-progreso/YYYY-MM-DD/  ← approved (instrucción derivada)
├── 03-completadas/YYYY-MM-DD/  ← done
├── 04-archivadas/YYYY-MM-DD/   ← archivada
├── 05-canceladas/YYYY-MM-DD/   ← rejected
└── 06-listas-para-eliminar/    ← para-eliminar
```

El árbol es el índice; vista viva de pendientes: `python3 docs/scripts/decisiones/decisiones.py scan`.

(En Windows: `py -3` en lugar de `python3`.)

Estados (`status`): `pending` (01) | `approved` (02) | `done` (03) | `archivada` (04) | `rejected` (05) | `para-eliminar` (06).

Tipos: `deuda-tecnica` | `refactor` | `diseno` | `tests` | `docs` | `perf` | `seguridad` | `bug`.

Crear desde [_PLANTILLA-propuesta.md](_PLANTILLA-propuesta.md). Revisar: [_PLANTILLA-revisar-propuesta.md](_PLANTILLA-revisar-propuesta.md). Protocolo: [_PROTOCOLO.md](_PROTOCOLO.md).
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
