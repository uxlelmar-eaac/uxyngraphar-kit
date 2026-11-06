# Manuales operativos

Activado con «usa el paquete manuales» / «sigue el protocolo runbook» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/manuales/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Consulta manuales: `python3 $S/comun/fichas.py listar manual`. Nuevo: `python3 $S/comun/fichas.py nueva manual --slug <slug> --titulo "…"`.
4. Si tu cambio altera cómo se despliega, configura u opera algo, actualiza el manual afectado en la misma tarea.
5. Antes de terminar: `python3 $S/comun/verificar.py`.

Trabajo: `uxyngraphar/trabajo/manuales/`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Pasos ejecutables:** comandos exactos, en orden, con el resultado esperado de cada uno.
2. **Sin secretos:** variables como `<PLACEHOLDER>` y de dónde se obtienen, nunca valores.
3. **Vivo:** un cambio que altera un procedimiento actualiza su manual en la misma tarea; anota la fecha en «Última verificación».
4. **`vigente` lo decide una persona** tras probarlo; el agente deja `borrador`.
5. **Un procedimiento por manual**; enlaza otros en lugar de copiarlos.
6. Incluye siempre «Cómo revertir» cuando el procedimiento cambia el sistema.
