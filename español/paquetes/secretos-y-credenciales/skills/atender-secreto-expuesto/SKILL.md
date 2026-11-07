---
name: atender-secreto-expuesto
description: Gestiona un secreto real encontrado en el repositorio sin propagarlo, avisa a la persona con lo necesario para rotarlo y lo sustituye en el código.
resuelve: [secretos-expuestos-sin-rotar]
---

# Atender secreto expuesto

## Cuándo usarla

- En la fase `atender-incidente`, cuando `secretos.py` encuentra un valor que parece real.
- Cuando la persona avisa de que un secreto se ha publicado.

## Pasos

1. No copies el valor a ningún sitio (respuesta, ficha, commit, log). Refiérete a él por ruta, línea y la muestra enmascarada de `secretos.py`.
2. Averigua si está en el historial sin escribir el valor en ningún comando: `git status --short <ruta>` dice si el archivo está versionado y `git log --oneline -- <ruta>` qué commits lo tocaron. La búsqueda exacta (`git log -S '<valor>'`) exige teclear el valor: pídesela a la persona.
3. Avisa a la persona con: ruta, línea, tipo detectado, si está en el historial y si la rama llegó a un remoto.
4. Sustituye el valor en el código con la skill `sustituir-por-variable-de-entorno`.
5. Recuerda a la persona lo que solo ella puede hacer (`referencia/si-aparece-un-secreto.md`): revocar la credencial en el proveedor y emitir una nueva; si llegó a un remoto, decidir con el equipo si se limpia el historial.
6. Vuelve a ejecutar `python3 $P/scripts/secretos.py <ruta>` hasta que salga con código 0.

## Resultado

- La persona está avisada con datos suficientes para rotar, el código ya no tiene el valor y nada del proceso lo ha copiado a otro sitio.
