# Caso: revisar la accesibilidad del alta

## Pedido

«Usa el paquete pautas-de-accesibilidad: nos dicen que el alta no se puede usar con teclado; revísala.» El proyecto no tiene `ACCESIBILIDAD.md` todavía.

## Recorrido

**revisar.** Se copia `$P/plantillas/ACCESIBILIDAD.md` a `uxyngraphar/trabajo/pautas-de-accesibilidad/ACCESIBILIDAD.md` y se abre la sección `## Revisión 2026-11-06 — /signup`. Tarea principal: «crear una cuenta con correo y contraseña». Lighthouse móvil, mediana de 3: 81. Con `revisar-accesibilidad` salen tres barreras:

```
| 1 | /signup | teclado     | El botón «Crear cuenta» no recibe foco  | Tab desde contraseña lo salta; `src/signup/form.tsx:120` | bloqueante | Usar `<Button>` en lugar de `div` con onClick | | pendiente |
| 2 | /signup | formularios | El error solo pone el borde en rojo     | enviar vacío; `src/signup/form.tsx:88`                   | grave      | Texto bajo el campo con `aria-live="polite"`  | | pendiente |
| 3 | /signup | contraste   | Texto de ayuda gris sobre blanco        | 3.1:1 medido sobre `--color-texto-suave`                 | grave      | Oscurecer el token `--color-texto-suave`      | | pendiente |
```

No hay lector de pantalla en el entorno: se dice en «Notas». El agente se detiene y resume: una bloqueante y dos graves; la 3 cambia un token compartido, que afecta a todo el sitio.

La persona marca «sí» en la 1 y la 2. De la 3 dice que el cambio de token lo decidirá diseño: la deja `pendiente` con la razón en «Notas».

**corregir.** El `div` pasa a ser el `<Button>` existente; el error pasa a texto junto al campo, anunciado. La 3 no se toca.

**comprobar.** Mismo recorrido con teclado: el botón recibe foco y se puede enviar. Enviar vacío muestra y anuncia el error. Lighthouse móvil, mediana de 3: 92. Las barreras 1 y 2 pasan a `corregida`; `verificar.py` sin errores. Se informa a la persona: 2 corregidas, 1 pendiente de diseño, 81 → 92.

## Resultado

- `ACCESIBILIDAD.md` con la revisión del alta: dos barreras `corregida` y una `pendiente` con su razón.
- Solo se tocó `src/signup/form.tsx`; el token de color sigue igual hasta que decida diseño.
