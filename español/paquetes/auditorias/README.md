# Auditorías

Activado con «usa el paquete auditorias» / «sigue el protocolo auditoria» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/auditorias/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Abre la auditoría: `python3 $S/comun/fichas.py nueva auditoria --slug <slug> --titulo "…"`; define alcance y preguntas **antes** de investigar. Pásala a `en-curso` al empezar.
4. Investiga solo dentro del alcance; cada hallazgo con evidencia (`ruta:línea`, comando, medición) y severidad.
5. Cierra con conclusiones y promociones propuestas; `fichas.py estado <id> cerrada`.
6. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-auditorias.py`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Auditar no es arreglar.** Una auditoría no modifica código ni documentación del producto; solo produce la ficha.
2. **Alcance y preguntas primero.** Sin ellos no se investiga.
3. **Evidencia o no es hallazgo.** Cada hallazgo cita `ruta:línea`, comando reproducible o medición. Las opiniones van en «Notas».
4. **Severidad** obligatoria por hallazgo: `critica`, `alta`, `media`, `baja` o `info` (según `ajustes.severidades`).
5. **`findings_count`** coincide con el número de hallazgos de la tabla.
6. **Promociones, no acciones.** Lo que haya que cambiar se propone como ADR, instrucción, mejora o actualización de documentación; lo decide una persona.
