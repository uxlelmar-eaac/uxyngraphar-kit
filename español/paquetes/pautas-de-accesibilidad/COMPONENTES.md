# Componentes

Las piezas que define el paquete. Viven en `uxyngraphar/trabajo/pautas-de-accesibilidad/ACCESIBILIDAD.md`, que nace de `plantillas/ACCESIBILIDAD.md`.

## Documento de accesibilidad

`ACCESIBILIDAD.md`: documento único del trabajo (no es ficha). Lleva una sección `## Revisión <AAAA-MM-DD> — <pantallas>` por revisión, la más reciente arriba. Se crea copiando la plantilla si no existe.

## Revisión

Una pasada sobre unas pantallas concretas: pantallas y tarea principal, herramientas y condiciones (Lighthouse móvil, axe, teclado, lector de pantalla), puntuación automática antes y después, tabla de barreras y notas.

## Barrera

Fila de la tabla «Barreras»: número, pantalla, criterio, barrera (como la vive el usuario), evidencia, gravedad, corrección propuesta, «Aprobada» y estado.

## Criterio

El punto de `referencia/accesibilidad.md` que se incumple: `contraste`, `teclado`, `foco`, `objetivos`, `semantica`, `formularios`, `medios`, `movimiento` o `zoom`.

## Gravedad

`bloqueante` (impide completar la tarea), `grave` (la completa con mucho esfuerzo o con ayuda) o `menor` (molesta, pero se completa).

## Estado de una barrera

`pendiente` (registrada), `corregida` (corregida y comprobada con la misma herramienta), `aceptada` (la persona decide no corregirla y lo deja dicho en «Notas»).
