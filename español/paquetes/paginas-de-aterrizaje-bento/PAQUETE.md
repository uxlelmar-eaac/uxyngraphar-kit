# Páginas de aterrizaje bento

Diseña y construye páginas de aterrizaje con mosaico bento en las que el tamaño de cada celda comunica su importancia, hay un solo objetivo y la página no se publica sin comprobar accesibilidad y rendimiento.

## Qué resuelve

Una página de aterrizaje bento falla de formas previsibles: varios CTA compiten, todas las celdas pesan lo mismo, los textos no caben en móvil, la protagonista acaba en tercer lugar al apilar y se publica sin mirar el contraste ni la carga de imágenes. El paquete obliga a escribir antes del código una ficha con objetivo, audiencia y un mosaico explícito (tamaño, prioridad, título, mensaje, CTA y medio de cada celda) sobre una rejilla de columnas fija, y comprueba con `verificar-bento.py` que el mosaico llena filas, tiene un único CTA primario, una protagonista mayor que el resto y textos breves, y que la checklist de publicación está completa antes de pasar a revisión.

## Problemas que cubre

- `paginas-sin-objetivo-unico`: varios objetivos o más de un CTA principal en la misma página.
- `mosaico-sin-jerarquia`: tamaños que no reflejan la importancia, prioridades repetidas, tamaños fuera de rejilla o huecos.
- `celdas-sobrecargadas`: más de una idea por celda, textos largos o medios sin texto alternativo.
- `orden-movil-incorrecto`: apilado móvil por posición visual en lugar de por prioridad.
- `publicacion-sin-comprobar`: publicar sin comprobar contraste, foco, carga, saltos de diseño ni el destino del CTA.

## Fuera de alcance

- Evaluar y mejorar la usabilidad de pantallas existentes de la aplicación: `evaluaciones-de-usabilidad`.
- La ficha viva de cada página o ruta de la interfaz: `paginas-de-interfaz`.
- Cambiar el sistema de diseño global u otras páginas del sitio: no lo cubre el kit.
- Páginas de aterrizaje con otra composición (secciones largas, narrativa de una columna): no lo cubre el kit.
- Estrategia de campaña (SEO, analítica, pruebas A/B, redacción publicitaria de fondo): no lo cubre el kit.

## Cuándo usarlo

- Al crear una página de aterrizaje nueva para un producto, una función o una campaña con una acción clara.
- Al rehacer una página de aterrizaje existente en formato de mosaico.
- Al revisar una página bento antes de publicarla.

## Cuándo no usarlo

- Para páginas de contenido largo (blog, documentación, términos legales).
- Para pantallas de la aplicación con tareas de usuario: eso es `evaluaciones-de-usabilidad`.
- Si la página no tiene una única acción principal que el visitante deba hacer.

## Entradas y salidas

- Entradas: el pedido (producto, campaña, acción esperada del visitante), la audiencia, los contenidos y medios disponibles y los ajustes de `uxyngraphar/trabajo/paginas-de-aterrizaje-bento/ajustes.json`.
- Salidas: una ficha `LAN-…` en `uxyngraphar/trabajo/paginas-de-aterrizaje-bento/<estado>/` con objetivo, audiencia, mosaico, orden móvil y checklist marcada; y la página construida en el código siguiendo ese mosaico.

## Paquetes complementarios

- `paginas-de-interfaz`: la ficha viva de la ruta de la página, una vez construida.
- `evaluaciones-de-usabilidad`: evaluar con métricas la página ya publicada si no convierte.
- `revision-humana`: recoge las páginas en `revision` que esperan la decisión de publicar.
