# Frontmatter — evolución (`46-evolucion-documentacion/`)

Ruta: `46-evolucion-documentacion/<estado>/YYYY-MM-DD/EVO-YYYYMMDD-slug.md`.
Estados: `01` (`pending`) · `02` (`approved`) · `03` (`done`) · `04`
(`archivada`) · `05` (`rejected`) · `06` (`para-eliminar`).

**Alcance (R-18):** solo propuestas/cambios del **sistema documental
completo** (pack, taxonomía, convenciones, plantillas, procesos,
metodología). Nunca documentación funcional de un proyecto.

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|-------|
| `id` | string | sí | `EVO-YYYYMMDD-slug` |
| `status` | enum | sí | `pending` \| `approved` \| `rejected` \| `done` \| `archivada` \| `para-eliminar` |
| `tipo` | enum | sí | `cobertura` \| `proceso` \| `taxonomia` \| `plantilla` \| `herramienta-pack` |
| `impacto` | enum | sí | `general` \| `servidor` \| `cliente` \| `ambos` |
| `prioridad` | enum | no | `ahora` \| `despues` \| `algun-dia` |
| `detected_in` | string | no | Instrucción o `revision-humana` |
| `propuesta_cambio` | string[] | no | Paths del pack a modificar |
| `instruction_derivada` | string | no | Tras aprobación humana |
| `exportada_al_pack` | fecha | no | La escribe `scripts/exportar-evo.py --marcar` al enviarla al pack fuente |
| `ajuste_local` | string | no | Id del ajuste `AJ-*` que la aplica en este proyecto; lo escribe `scripts/ajustes.py crear` (R-25) |
| `feedback_enviada` | fecha | no | Último envío con `scripts/feedback.py enviar` |
| `feedback_huella` | string | no | Huella de lo enviado: si la ficha cambia, el siguiente envío la incluye otra vez |
