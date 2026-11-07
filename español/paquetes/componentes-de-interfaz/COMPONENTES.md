# Componentes

Las piezas que define el paquete. Viven en `uxyngraphar/trabajo/componentes-de-interfaz/INTERFAZ.md`, que nace de `plantillas/INTERFAZ.md`.

## Documento de interfaz

`INTERFAZ.md`: documento único del trabajo (no es ficha). Tiene el inventario (tokens y componentes compartidos) y una sección `## Revisión <AAAA-MM-DD> — <pantallas>` por revisión, la más reciente arriba. Se crea copiando la plantilla si no existe.

## Inventario

Dónde están los tokens del proyecto (archivo y escalas: color, espaciado, tipografía, radios, sombras) y qué componentes compartidos hay, con su ruta y su propósito. Se actualiza al empezar cada revisión.

## Hallazgo

Fila de la tabla «Hallazgos»: número, pantalla, tipo, hallazgo, evidencia, corrección (token o componente existente), «Aprobada» y estado (`pendiente`, `corregido` o `aceptado`).

## Tipo de hallazgo

`valor-suelto` (color, tamaño, fuente, radio o sombra escritos a mano), `duplicado` (dos componentes para un mismo propósito), `estado-sin-cubrir` (falta alguno de los ocho estados) o `jerarquia` (más de una acción primaria, secundarias que compiten).

## Estados de un componente

Los ocho que todo componente interactivo cubre: normal, hover, foco visible, activo, deshabilitado, carga, vacío y error.
