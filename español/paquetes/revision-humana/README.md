# Revisión humana

Activado con «usa el paquete revision-humana» / «sigue el protocolo revision de pendientes» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/revision-humana/scripts`.

Recorre los paquetes instalados y reúne las fichas que esperan una decisión de una persona: instrucciones por aprobar, ADR propuestas, mejoras y EVO pendientes, reglas y ajustes propuestos, manuales en borrador… Cada paquete declara qué status esperan (`espera_humano`, o el inicial si tiene `solo_humano`).

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Lista lo pendiente: `python3 $S/revision.py pendientes` (de lo más antiguo a lo más nuevo, con el comando que debe ejecutar la persona).
4. Prepara la hoja de decisiones: `python3 $S/revision.py preparar` → `uxyngraphar/trabajo/revision-humana/REVISION.md`. Resume a la persona qué decide en cada fila, sin decidir por ella.
5. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-revision.py`.

Persona: escribe en la columna «Decisión» de `REVISION.md` un status de «Opciones» (o `posponer`) y ejecuta `python3 $S/revision.py aplicar --humano`. Cada decisión se aplica con el comando propio del paquete (por ejemplo, aprobar una instrucción comprueba su alcance).

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **El agente prepara, la persona decide.** Nunca escribas en la columna «Decisión» ni ejecutes `aplicar`.
2. **Estado real:** una ficha que espera decisión afirma que su efecto no está aplicado. Si ya lo está, avisa: el status es incorrecto.
3. **Contexto suficiente, no más:** para cada fila, una o dos líneas con qué se decide y qué pasa si se aprueba; enlaza la ficha en lugar de copiarla.
4. **Lo antiguo primero:** las fichas con más de `dias_aviso` (14) días esperando se señalan; propón decidirlas o cerrarlas.
