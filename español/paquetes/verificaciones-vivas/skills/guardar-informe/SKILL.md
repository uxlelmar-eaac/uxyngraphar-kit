---
name: guardar-informe
description: Guarda el resultado de unas revisiones como auditoría de auditorias-tecnicas (si está instalado) o como INFORME-<fecha>-<revisiones>.md en el trabajo del paquete.
resuelve: [fichas-desalineadas-del-codigo, referencias-rotas, decisiones-incumplidas, manuales-sin-verificar, flujos-basicos-rotos]
---

# Guardar informe

## Cuándo usarla

- La persona quiere dejar constancia de una revisión (fase `informar`).
- Los hallazgos se van a promover a otros flujos desde una auditoría.

## Pasos

1. Ejecuta las mismas revisiones con `--informe`: `python3 $P/scripts/vivas.py <revisión>… --informe` (añade `--ejecutar` si incluye `humo` ejecutado).
2. Con `auditorias-tecnicas` instalado nace `AUD-<fecha>-vivas-<revisiones>` con status `activa`, `findings_count`, `severidad` (la peor de los hallazgos) y la tabla, el método y las notas rellenados. Si ya existe una del mismo día y revisiones, se añade un sufijo `-2`, `-3`…
3. Sin ese paquete, se escribe `uxyngraphar/trabajo/verificaciones-vivas/INFORME-<AAAAMMDD>-<revisiones>.md` con método, tabla y notas.
4. La salida termina con `informe: <ruta>`; dásela a la persona.
5. No edites la tabla generada para quitar hallazgos: si alguno es ruido, explícalo en la respuesta.

## Resultado

- Una auditoría o un informe con la tabla de hallazgos, reproducible con el comando que figura en «Método».
