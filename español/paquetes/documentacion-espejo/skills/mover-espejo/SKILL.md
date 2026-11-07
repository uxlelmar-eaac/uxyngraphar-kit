---
name: mover-espejo
description: Mueve o renombra el espejo de un archivo o carpeta que cambia de ubicación, en la misma tarea, para que no quede huérfano ni se pierda su contenido.
resuelve: [espejos-huerfanos, espejos-desfasados]
---

# Mover espejo

## Cuándo usarla

- Un archivo o carpeta de código se mueve o se renombra.
- `espejo.py huerfanos` lista un espejo cuyo código sigue existiendo en otra ruta.

## Pasos

1. Calcula las dos rutas espejo: `src/orders/service.ts` → `uxyngraphar/trabajo/documentacion-espejo/src/orders/service.md`; una carpeta → su `README.md`.
2. Mueve el archivo del espejo a la ruta nueva (crea las carpetas que falten). En un repo con git, `git mv` conserva el historial. Para una carpeta, mueve la carpeta entera del espejo.
3. Actualiza la cabecera (la ruta tras «Espejo de:» y la fecha) y las tablas de «Interacciones» o «Contenido» que citen la ruta antigua, también en los espejos de la carpeta de origen y de destino.
4. Comprueba con `python3 $P/scripts/espejo.py ver <ruta-nueva>` que se encuentra y con `python3 $P/scripts/espejo.py huerfanos` que la antigua ya no aparece.

## Resultado

- El espejo vive en la ruta nueva con su contenido intacto y la cabecera al día; la antigua no queda huérfana.
