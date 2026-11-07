---
fase: atender-incidente
resuelve: [secretos-expuestos-sin-rotar]
skills: [atender-secreto-expuesto]
---

# Fase: atender incidente

Solo si aparece un secreto que parece real (no un placeholder ni un dato de prueba evidente). Si no, esta fase no se recorre.

## Objetivo

Que un secreto real expuesto acabe revocado por la persona, no solo borrado del archivo, y que no se propague durante la gestión.

## Entradas

- El hallazgo de `secretos.py`: ruta, línea, tipo y muestra enmascarada.
- La guía `referencia/si-aparece-un-secreto.md`.

## Pasos

1. Detén la tarea en curso.
2. Aplica la skill `atender-secreto-expuesto`: aviso a la persona con ruta, línea, tipo y si está en el historial, y sustitución en el código.
3. Espera a que la persona confirme la rotación; no la des por hecha.
4. Vuelve a `escanear` y retoma la tarea solo cuando la persona lo indique.

## Criterio de salida

- La persona está avisada con los datos del incidente, el código ya no contiene el valor y `secretos.py` sale con código 0.
- La rotación y la limpieza del historial quedan en manos de la persona (confirmadas o pendientes, dicho explícitamente).
