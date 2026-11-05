# Si aparece un secreto real

1. **Detente.** No sigas con la tarea hasta resolverlo.
2. **No lo copies** a ningún otro sitio (chat, ficha, commit, log). Refiérete a él por ruta y línea.
3. **Avisa a la persona** con: ruta, línea, tipo detectado y si ya está en el historial de git (`git log -S` lo dice; no imprimas el valor).
4. **Sustituye en el código** por `<PLACEHOLDER>` o una variable de entorno, y documenta la variable en la plantilla (`.env.example`).
5. **Rotación (persona):** revocar la credencial en el proveedor y emitir una nueva. Borrar del archivo no la invalida si ya se publicó.
6. **Historial (persona):** si llegó a un remoto, limpiar el historial (`git filter-repo` o equivalente) es decisión de la persona y del equipo.
7. Vuelve a ejecutar `scripts/escanear.py` hasta que salga con código 0.
