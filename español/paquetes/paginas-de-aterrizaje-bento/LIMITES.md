# Límites

Se cumplen en todo el trabajo del paquete. Valores ajustables (columnas, límites) en `uxyngraphar/trabajo/paginas-de-aterrizaje-bento/ajustes.json`.

1. **Ficha primero.** Ninguna página de aterrizaje se construye sin ficha con Objetivo, Audiencia y Mosaico. La ficha manda: si el código y la ficha difieren, se corrige uno de los dos antes de terminar.
2. **Una página, un objetivo, un CTA principal.** Exactamente una celda lleva el CTA `primario`; las demás, `secundario` o `-`.
3. **Mosaico en rejilla de `columnas` (4 por defecto).** Tamaños permitidos (`ancho x alto`): `1x1`, `2x1`, `1x2`, `2x2`, `4x1`. Entre `celdas_min` y `celdas_max` celdas; como mucho `max_2x2` celdas `2x2` (la protagonista). La suma de áreas debe llenar filas completas: sin huecos.
4. **Jerarquía explícita.** Cada celda tiene prioridad única 1..n; la 1 es la protagonista y ocupa la celda más grande. En móvil el mosaico se apila **en orden de prioridad**, no en orden visual.
5. **Una idea por celda.** Título ≤ `palabras_titulo` palabras; mensaje ≤ `palabras_mensaje` palabras. Si no cabe, son dos celdas o sobra.
6. **Medios con texto alternativo.** Columna Medio: `-`, `img: <alt>`, `video: <descripción>` o `icono` (decorativo, `aria-hidden`). Sin alt no hay imagen.
7. **Accesibilidad no negociable:** contraste WCAG AA, foco visible en todo lo interactivo, orden de tabulación = orden de prioridad, animaciones que respetan `prefers-reduced-motion`, y la celda entera clicable con un único enlace con nombre accesible.
8. **Rendimiento:** la imagen de la celda protagonista se carga con prioridad; el resto, diferida; todo medio con dimensiones reservadas (sin saltos de diseño); sin fuentes ni scripts que bloqueen el primer pintado.
9. **Publicar es humano.** El agente deja la ficha en `revision` con la checklist completa; `publicada` lo marca una persona (`--humano`).
10. **Alcance.** El paquete gobierna la página de aterrizaje y su ficha; no cambia el sistema de diseño global ni otras páginas sin que la persona lo pida.

## Cuándo detenerse y preguntar

- El pedido tiene dos objetivos o dos acciones principales: ¿cuál es el CTA primario?
- El contenido no cabe en `celdas_max` celdas ni en los límites de palabras sin perder algo importante.
- Falta un medio para la protagonista o su texto alternativo no se puede deducir.
- Construir la página exige cambiar tokens o componentes globales.
- Al pasar a `revision`: la persona revisa y decide si publica.
