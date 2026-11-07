# Límites

Se cumplen en todo el trabajo, con este paquete activo o no, mientras esté instalado.

1. **Nunca edites un paquete instalado.** Lo que no encaja se adapta con un ajuste local en `uxyngraphar/trabajo/adaptaciones-de-paquetes/ajustes-locales/`.
2. **Precedencia:** un ajuste `activo` manda sobre `aplica_a` de su paquete, solo en este proyecto y solo en lo que dice. El resto del archivo sigue valiendo.
3. **Por revisar no es retirado:** si un ajuste está «por revisar» (el archivo del paquete cambió), síguelo igualmente y avisa a la persona al cerrar.
4. **Solo una persona** activa, revisa o retira un ajuste (`adaptaciones.py aprobar-ajuste … --humano`, `fichas.py estado AJL-… retirado --humano`). El agente solo propone.
5. **No edites un ajuste activo.** Si hay que cambiarlo, propón uno nuevo y que una persona retire el anterior.
6. **Un ajuste es temporal:** cuando el paquete incorpora el cambio, una persona lo retira (`retirado`), que queda como historia.
7. **Un ajuste apunta a un archivo que existe:** `uxyngraphar/paquetes/<paquete>/<aplica_a>`; uno por archivo y por motivo.

## Cuándo detenerse y preguntar

- Un ajuste «por revisar» contradice lo que ahora dice el archivo del paquete.
- Dos ajustes activos sobre el mismo archivo se contradicen, o un ajuste contradice una regla activa de `reglas-del-proyecto`.
- El ajuste que hace falta cambiaría lo que el paquete garantiza (sus límites): confirma con la persona antes de proponerlo.
- La tarea no puede seguir sin un ajuste que aún está `propuesto`: espera a que una persona lo active.
