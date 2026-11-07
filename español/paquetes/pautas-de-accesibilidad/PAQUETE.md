# Pautas de accesibilidad

Revisa las pantallas del pedido contra el mínimo WCAG 2.2 AA, deja cada barrera con su criterio y su evidencia, corrige solo lo que una persona aprueba y comprueba con la misma herramienta que nada quedó peor.

## Qué resuelve

La accesibilidad suele revisarse al final, con una pasada automática que no ve el teclado ni el foco, o no revisarse. Este paquete fija un mínimo comprobable (`referencia/accesibilidad.md`), obliga a recorrer la tarea principal solo con teclado además de la herramienta automática, registra cada barrera en `ACCESIBILIDAD.md` con el criterio que incumple, su evidencia y la corrección propuesta, y no da una corrección por buena hasta repetir la comprobación.

## Problemas que cubre

- `barreras-de-accesibilidad`: incumplimientos de WCAG 2.2 AA (contraste, teclado, foco, objetivos táctiles, etiquetas, texto alternativo, movimiento, zoom).

## Fuera de alcance

- Evaluar la usabilidad de un flujo con heurísticas, propuesta aprobada y métricas antes/después: `evaluaciones-de-usabilidad`.
- Revisar que las pantallas reutilicen tokens y componentes y cubran todos sus estados: `componentes-de-interfaz`.
- Comprobar una página de aterrizaje bento antes de publicarla (su checklist ya incluye contraste y foco): `paginas-de-aterrizaje-bento`.
- La ficha viva de cada página o ruta de la interfaz: `paginas-de-interfaz`.
- Certificar la conformidad legal o formal (VPAT, declaraciones de accesibilidad, nivel AAA): no lo cubre el kit.
- Pruebas moderadas con personas con discapacidad: no lo cubre el kit; sus resultados sí pueden ser evidencia.

## Cuándo usarlo

- Cuando la persona pide revisar o mejorar la accesibilidad de unas pantallas o un flujo.
- Antes de entregar una pantalla nueva o rehecha.
- Cuando llega una queja concreta de accesibilidad («no puedo usar el formulario con teclado»).

## Cuándo no usarlo

- Para decidir si una pantalla es fácil de usar en general: `evaluaciones-de-usabilidad`.
- Para un sitio sin interfaz visual (una API, una biblioteca).

## Entradas y salidas

- Entradas: las pantallas del pedido (código y la app en marcha), una herramienta automática (Lighthouse o axe), el teclado y, si existe, un lector de pantalla.
- Salidas: `uxyngraphar/trabajo/pautas-de-accesibilidad/ACCESIBILIDAD.md` con las revisiones, sus barreras y su estado; y, tras la aprobación, las correcciones en el código.

## Paquetes complementarios

- `evaluaciones-de-usabilidad`: si existe `uxyngraphar/trabajo/evaluaciones-de-usabilidad/`, una evaluación `UXE-…` aprobada sobre las mismas pantallas cuenta como aprobación de las filas `A11Y` que recoge; sus fichas leen `ACCESIBILIDAD.md` como evidencia.
- `componentes-de-interfaz`: una barrera de un componente compartido (foco, contraste de un token) se corrige en el componente, no en cada pantalla.
- `paginas-de-interfaz`: la ficha de la página corregida se actualiza allí.
