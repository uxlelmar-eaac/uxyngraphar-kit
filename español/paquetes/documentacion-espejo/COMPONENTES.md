# Componentes

Las piezas que define el paquete. Rutas por defecto; el proyecto las ajusta en `ajustes.json`.

## Espejo de archivo

`uxyngraphar/trabajo/documentacion-espejo/<ruta-del-archivo-sin-extension>.md`. Nace de `plantillas/archivo.md` con el nombre, la ruta, las líneas y la fecha ya puestas. Secciones: «Rol» (una frase), «Responsabilidades», «Interacciones» (tabla con qué otros archivos o servicios y cómo) y «Puntos de extensión».

## Espejo de carpeta

`uxyngraphar/trabajo/documentacion-espejo/<ruta-de-la-carpeta>/README.md`. Nace de `plantillas/carpeta.md`. Secciones: «Propósito», «Contenido» (tabla de elementos y su rol) y «Fronteras» (de qué depende y quién la usa). Toda carpeta de módulo lo lleva.

## Ruta espejo

La correspondencia entre código y espejo es solo por ruta: misma ruta relativa a la raíz de la app, con la extensión cambiada a `.md`. Por eso dos archivos con el mismo nombre y distinta extensión en una carpeta (`index.ts`, `index.css`) comparten espejo.

## Cobertura

Porcentaje de elementos de código (carpetas bajo `raices` más archivos con una extensión de `extensiones`, menos lo que casa con `excluir`) que tienen espejo. `espejo.py mapa` la muestra; `verificar-espejo.py` falla si queda bajo `cobertura_minima`.

## Espejo huérfano

Espejo bajo una raíz cuyo archivo (mismo nombre sin extensión en la carpeta) o carpeta ya no existe. Siempre es un error. Los archivos que empiezan por `_` en el espejo no se revisan: sirven para notas propias de la persona.
