# Componentes de interfaz

Mantiene las pantallas consistentes con lo que el proyecto ya tiene: tokens y componentes compartidos antes que valores sueltos, un componente por propósito y los ocho estados cubiertos en cada componente interactivo.

## Qué resuelve

Con el tiempo, cada pantalla acaba con su propio azul, su propio margen y su propio botón primario, y los estados de foco, carga, vacío o error se olvidan. Este paquete deja en `INTERFAZ.md` dónde están los tokens y los componentes compartidos del proyecto, revisa las pantallas del pedido contra ellos y contra los estados de `referencia/consistencia-ui.md`, anota cada hallazgo con su `ruta:línea` y el token o componente que lo resuelve, y corrige solo lo que una persona aprueba.

## Problemas que cubre

- `interfaz-inconsistente`: valores y componentes sueltos que no reutilizan los tokens y componentes existentes, o estados sin cubrir.

## Fuera de alcance

- Evaluar la usabilidad de un flujo con heurísticas, propuesta aprobada y métricas antes/después: `evaluaciones-de-usabilidad`.
- Revisar la interfaz contra WCAG 2.2 AA: `pautas-de-accesibilidad`. Aquí solo se comprueba que el foco tenga un estado visible.
- Decidir y documentar qué ve el usuario en cada página cuando carga, está vacía o falla: `paginas-de-interfaz`. Aquí se comprueba que cada componente tenga esos estados, no qué decide la página.
- Diseñar y construir páginas de aterrizaje con mosaico bento: `paginas-de-aterrizaje-bento`.
- Crear o rediseñar el sistema de diseño global (paleta, escala tipográfica, librería de componentes): no lo cubre el kit.

## Cuándo usarlo

- Cuando la persona pide revisar o unificar el aspecto de unas pantallas.
- Antes de crear un componente nuevo, para comprobar si ya existe uno que sirva.
- Al tocar un componente interactivo, para cubrir sus ocho estados.

## Cuándo no usarlo

- Si el proyecto no tiene tokens ni componentes compartidos y la persona quiere crearlos: eso es el sistema de diseño global.
- Para decidir si una pantalla es fácil de usar en general: `evaluaciones-de-usabilidad`.

## Entradas y salidas

- Entradas: las pantallas del pedido, los tokens del proyecto (tema, variables CSS, archivo de diseño) y su carpeta de componentes compartidos.
- Salidas: `uxyngraphar/trabajo/componentes-de-interfaz/INTERFAZ.md` con el inventario de tokens y componentes y las revisiones con sus hallazgos; y, tras la aprobación, las correcciones en el código.

## Paquetes complementarios

- `evaluaciones-de-usabilidad`: si existe `uxyngraphar/trabajo/evaluaciones-de-usabilidad/`, una evaluación `UXE-…` aprobada sobre las mismas pantallas cuenta como aprobación de las filas `UI` que recoge; sus fichas leen `INTERFAZ.md` como evidencia.
- `pautas-de-accesibilidad`: el contraste de un token o el foco de un componente compartido se revisa allí con el criterio WCAG.
- `paginas-de-interfaz`: la ficha de la página corregida se actualiza allí.
