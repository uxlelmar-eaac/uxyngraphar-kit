# Evolución documental — índice
<!-- uxyngraphar:inicio -->

Bandeja de **meta-mejoras del sistema documental completo**: estructura, taxonomía, convenciones, plantillas, procesos y metodología del pack. **No** es deuda de producto (→ `45-mejoras-propuestas/`) ni documentación funcional de un proyecto (R-18).

## Organización (R-17)

```
46-evolucion-documentacion/
├── 01-pendientes/YYYY-MM-DD/   ← pending
├── 02-en-progreso/YYYY-MM-DD/  ← approved
├── 03-completadas/YYYY-MM-DD/  ← done
├── 04-archivadas/YYYY-MM-DD/   ← archivada
├── 05-canceladas/YYYY-MM-DD/   ← rejected
└── 06-listas-para-eliminar/    ← para-eliminar
```

## Documentos clave (raíz, registros)

| Doc | Rol |
|-----|-----|
| [_PROTOCOLO.md](_PROTOCOLO.md) | Alcance oficial (R-18), estados, relación 45/40/35 |
| [matriz-cobertura-proyectos.md](matriz-cobertura-proyectos.md) | Mapa vivo: qué cubre el pack vs qué falta |
| [_PLANTILLA-cobertura.md](_PLANTILLA-cobertura.md) | Ficha tipo cobertura |
| [_PLANTILLA-proceso.md](_PLANTILLA-proceso.md) | Ficha tipo proceso faltante |

## Revisión de pendientes

Revisión de pendientes [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md): `python3 docs/scripts/decisiones/decisiones.py scan`

(En Windows: `py -3` en lugar de `python3`.)
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
