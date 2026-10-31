# Protocolo de auditorías

## Árbol (R-17)

```
40-auditorias/
├── 01-pendientes/YYYY-MM-DD/   ← pendiente
├── 02-en-progreso/YYYY-MM-DD/  ← activa (la IA puede leerlas si el área coincide)
├── 03-completadas/YYYY-MM-DD/  ← cerrada
├── 04-archivadas/YYYY-MM-DD/   ← archivada (no leer salvo cita explícita)
├── 05-canceladas/YYYY-MM-DD/   ← cancelada
└── 06-listas-para-eliminar/    ← para-eliminar
```

## Nomenclatura

Archivo: `AUD-YYYYMMDD-slug.md` dentro de `02-en-progreso/YYYY-MM-DD/`; nombre de archivo = `id` del frontmatter ([convenciones-frontmatter.md](../00-nucleo/convenciones-frontmatter.md)). Al cambiar de estado: **mover** el archivo a la carpeta de estado correspondiente conservando la carpeta de fecha.

## Ciclo

0. Antes de abrir cualquier AUD, leer [activas.md](activas.md). Al abrir:
   agregar su fila; al cerrar/cancelar: retirarla. Tope: 5 activas
   simultáneas (proponer cerrar antes de abrir otra).

1. Investigación no trivial → abrir audit en `02-en-progreso/YYYY-MM-DD/` al inicio (`status: activa`).
2. Si nace de instrucción: enlazar ids bidireccionales.
3. Hallazgos permanentes → promoción a canon / ADR / ficha endpoint.
4. Cerrar: `status: cerrada`, mover a `03-completadas/YYYY-MM-DD/`. Histórico: `04-archivadas/`.
5. `activa` > 14 días sin actualización → proponer cerrar o cancelar.
