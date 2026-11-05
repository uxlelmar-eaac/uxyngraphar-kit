# Auditorías — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Auditar no es arreglar.** Una auditoría no modifica código ni documentación del producto; solo produce la ficha.
2. **Alcance y preguntas primero.** Sin ellos no se investiga.
3. **Evidencia o no es hallazgo.** Cada hallazgo cita `ruta:línea`, comando reproducible o medición. Las opiniones van en «Notas».
4. **Severidad** obligatoria por hallazgo: `critica`, `alta`, `media`, `baja` o `info` (según `ajustes.severidades`).
5. **`findings_count`** coincide con el número de hallazgos de la tabla.
6. **Promociones, no acciones.** Lo que haya que cambiar se propone como ADR, instrucción, mejora o actualización de documentación; lo decide una persona.
