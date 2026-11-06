# Auditorías técnicas

Activado con «usa el paquete auditorias-tecnicas» / «sigue el protocolo auditoria tecnica» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/auditorias-tecnicas/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Mira las activas: `python3 $S/comun/fichas.py listar auditoria --status activa`. Si ya hay `max_activas`, cierra o pospón una (`pendiente`) antes de abrir otra.
   Abre la auditoría: `python3 $S/comun/fichas.py nueva auditoria --slug <slug> --titulo "…"` (nace `activa`); define alcance y preguntas **antes** de investigar. Una auditoría planificada para más adelante va a `pendiente`.
4. Investiga solo dentro del alcance; cada hallazgo con evidencia (`ruta:línea`, comando, medición) y severidad. Cada vez que avances, pon la fecha de hoy en `actualizado`.
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
7. **Pocas activas y vivas.** Como mucho `max_activas` (5) a la vez; una activa sin cambios en `dias_sin_cambios` (14) días se propone cerrar o pasar a `pendiente`.
8. **Nada se borra.** Una auditoría descartada va a `cancelada`; lo que una persona quiere retirar va a `para-eliminar` y de ahí al archivo histórico.
