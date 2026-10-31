# Protocolo — herramientas (cliente)

Catálogo de artefactos reutilizables (scripts npm, comandos, snippets, plantillas) que **agilizan** trabajo repetitivo en UI/BFF sin sustituir instrucciones para cambios de producto.

## Reglas

1. **Autorizadas:** creación **solo humana** (manual o promoción desde propuesta aprobada). `autorizadas/` es un registro **sin estados**.
2. **Propuestas:** creación **solo IA** dentro de instrucción o documentada en Resultado al cerrar; **nunca ejecutar** el código sugerido. Organización por estados (R-17):

```
35-herramientas/propuestas/
├── 01-pendientes/YYYY-MM-DD/   ← pending
├── 02-en-progreso/             ← en-evaluacion (humano revisando)
├── 03-completadas/             ← (la promovida sale a autorizadas/)
├── 04-archivadas/              ← archivada
├── 05-canceladas/YYYY-MM-DD/   ← rejected
└── 06-listas-para-eliminar/    ← para-eliminar
```

3. La IA solo escribe en `propuestas/01-pendientes/YYYY-MM-DD/` y registra el id en `herramientas_propuestas`.
4. **Promoción:** propuesta `approved` → humano crea ficha en `autorizadas/` (`source: human`); la propuesta original queda marcada y fuera de `01-pendientes/`.
5. **Rechazo:** mover a `propuestas/05-canceladas/YYYY-MM-DD/` con `status: rejected`.

## Fichas

- **Autorizada:** `_PLANTILLA-autorizada.md`; `status: authorized`; alcance permitido explícito.
- **Propuesta:** `_PLANTILLA-propuesta.md`; `status: pending`.

## Código asociado

- El código vive en el repo frontend; la ficha describe cuándo y cómo usarlo.

Ver guía [herramientas-autorizadas-vs-propuestas.md](../10-guias/herramientas-autorizadas-vs-propuestas.md).
