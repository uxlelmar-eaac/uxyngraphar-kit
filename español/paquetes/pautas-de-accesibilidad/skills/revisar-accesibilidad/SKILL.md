---
name: revisar-accesibilidad
description: Comprueba la tarea principal de unas pantallas contra el mínimo WCAG 2.2 AA (contraste, teclado, foco, objetivos táctiles, semántica, formularios, medios, movimiento, zoom) y anota cada barrera en ACCESIBILIDAD.md.
resuelve: [barreras-de-accesibilidad]
---

# Revisar accesibilidad

## Cuándo usarla

- En `revisar`, sobre cada pantalla del pedido.
- En `comprobar`, para repetir sobre lo corregido la misma comprobación que encontró la barrera.

## Pasos

1. Ejecuta una herramienta automática (Lighthouse o axe) sobre cada pantalla y anota la puntuación y las condiciones (dispositivo o emulación, número de ejecuciones) en la revisión.
2. Recorre la tarea principal solo con teclado: todo se alcanza, el orden es lógico, el foco se ve siempre y nada lo atrapa ni lo tapa.
3. Repasa cada punto de `referencia/accesibilidad.md` que aplique: contraste (4.5:1 texto, 3:1 grande y controles), objetivos de 24×24 px, elementos nativos, etiqueta visible por campo, errores en texto junto al campo, texto alternativo, `prefers-reduced-motion`, uso al 200 % y a 320 px.
4. Si hay lector de pantalla disponible, recorre con él la tarea principal; si no, dilo en «Notas».
5. Anota cada barrera como una fila de «Barreras»: el criterio es el código de `referencia/accesibilidad.md`; lo que impide completar la tarea es `bloqueante`. Formato:

   ```
   | 1 | /signup | teclado | El botón «Crear cuenta» no recibe foco | Tab desde el campo contraseña lo salta; `src/signup/form.tsx:120` | bloqueante | Usar `<Button>` en lugar de `div` con onClick | | pendiente |
   ```

## Resultado

- Barreras con criterio, evidencia, gravedad y corrección propuesta, y la puntuación automática anotada; o la constancia en «Notas» de que no se encontraron barreras.
