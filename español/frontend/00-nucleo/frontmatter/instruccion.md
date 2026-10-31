# Frontmatter — instrucción (`05-instrucciones/`)

Ruta: `05-instrucciones/<estado>/YYYY-MM-DD/<slug>.md`. Estados:
`01` (`draft`, `awaiting_approval`) · `02` (`approved`, `executing`) ·
`03` (`done`) · `04` (`archivada`) · `05` (`cancelled`) · `06`
(`para-eliminar`).

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|-------|
| `id` | string | sí | `YYYYMMDD-NNN-slug` |
| `status` | enum | sí | `draft` \| `awaiting_approval` \| `approved` \| `executing` \| `done` \| `cancelled` \| `archivada` \| `para-eliminar` \| `plantilla` |
| `areas` | string[] | sí | Al menos un área |
| `lectura_minima` | string[] | sí | Lista cerrada de paths |
| `anclas_codigo` | string[] | sí* | *Vacío solo en plantilla solo-docs |
| `espejo_actualizar` | string[] | sí* | *Obligatorio si hay `anclas_codigo` |
| `espejo_leer` | string[] | no | Default `[]` |
| `herramientas_propuestas` | string[] | no | Paths en `propuestas/` (ids) |
| `mejoras_propuestas` | string[] | no | Paths/ids en `45-mejoras-propuestas/` (máx. 3 al cerrar) |
| `evolucion_documentacion` | string[] | no | Paths/ids en `46-evolucion-documentacion/` (máx. 2 al cerrar) |
| `acto` | enum | sí* | *Obligatorio si `status` ≠ `plantilla`. `crear` \| `editar` \| `corregir` \| `mejorar-docs` \| `auditar` \| `adoptar` \| `operar` \| `revisar-pendientes`. Ver [ciclo-vinculante.md](../ciclo-vinculante.md) |
| `vinculos_entrada` | string[] | no | Origen: EVO, MEJ, AUD, instrucción previa |
| `excepciones_reglas` | string[] | no | Excepciones a reglas del proyecto: `"RP-NNN: motivo"`. Solo valen con la instrucción aprobada por una persona (`96-reglas-proyecto/_PROTOCOLO.md`) |
| `vinculos_salida` | string[] | no | Rellenar al `done`: ids + paths tocados |
| `presupuesto_max_archivos_codigo` | number | no | Default 5; `0` en solo-documentación; >5 solo con ampliación R-21 (tope `floor(5 × ampliacion_factor)`) |
| `presupuesto_max_docs` | number | no | Default 8; tope de `lectura_minima` + `espejo_leer` |
| `ampliacion_factor` | number | no* | *Obligatorio si hay >5 archivos de código y no se fracciona. `1.5`–`2` (R-21) |
| `ampliacion_justificacion` | string | no* | *Obligatorio con `ampliacion_factor`: qué se rompe si se entrega en partes de ≤5 |
| `ampliacion_aprobada_at` | datetime | no | Lo fija la aprobación humana (`decisiones.py apply`); sin él la ampliación no se ejecuta |
| `fraccion_de` | string | no | Id de la instrucción plan de la que es fracción (R-21, camino B) |
| `depende_de` | string[] | no | Ids de fracciones que deben cerrarse antes |
