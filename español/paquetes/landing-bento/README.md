# Landing page bento

Activado con «usa el paquete landing-bento» / «sigue el protocolo bento» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/landing-bento/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo) y, para diseñar, `docs/patrones-bento.md`.
3. Abre la ficha: `python3 $S/comun/fichas.py nueva landing --slug <slug> --titulo "…"`. Rellena **Objetivo, Audiencia y Mosaico antes de escribir código**; pásala a `en-curso` al empezar a construir.
4. Construye siguiendo el mosaico de la ficha: si al construir cambia una celda, cambia primero la ficha.
5. Cuando esté lista, marca la checklist (`docs/checklist-publicacion.md` explica cada punto) y pásala a `revision`. Publicar (`publicada`) lo decide una persona.
6. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-bento.py`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel. Valores ajustables (columnas, límites) en `uxyngraphar/trabajo/landing-bento/ajustes.json`.

1. **Ficha primero.** Ninguna landing se construye sin ficha con Objetivo, Audiencia y Mosaico. La ficha manda: si el código y la ficha difieren, se corrige uno de los dos antes de terminar.
2. **Una página, un objetivo, un CTA principal.** Exactamente una celda lleva el CTA `primario`; las demás, `secundario` o `-`.
3. **Mosaico en rejilla de `columnas` (4 por defecto).** Tamaños permitidos (`ancho x alto`): `1x1`, `2x1`, `1x2`, `2x2`, `4x1`. Entre `celdas_min` y `celdas_max` celdas; como mucho `max_2x2` celdas `2x2` (la protagonista). La suma de áreas debe llenar filas completas: sin huecos.
4. **Jerarquía explícita.** Cada celda tiene prioridad única 1..n; la 1 es la protagonista y ocupa la celda más grande. En móvil el mosaico se apila **en orden de prioridad**, no en orden visual.
5. **Una idea por celda.** Título ≤ `palabras_titulo` palabras; mensaje ≤ `palabras_mensaje` palabras. Si no cabe, son dos celdas o sobra.
6. **Medios con texto alternativo.** Columna Medio: `-`, `img: <alt>`, `video: <descripción>` o `icono` (decorativo, `aria-hidden`). Sin alt no hay imagen.
7. **Accesibilidad no negociable:** contraste WCAG AA, foco visible en todo lo interactivo, orden de tabulación = orden de prioridad, animaciones respetan `prefers-reduced-motion`, la celda entera clicable tiene un único enlace con nombre accesible.
8. **Rendimiento:** la imagen de la celda protagonista se carga con prioridad; el resto, diferida; todo medio con dimensiones reservadas (sin saltos de diseño); sin fuentes ni scripts que bloqueen el primer pintado.
9. **Publicar es humano.** El agente deja la ficha en `revision` con la checklist completa; `publicada` lo marca una persona (`--humano`).
10. **Alcance.** Este paquete gobierna la landing y su ficha; no cambia el sistema de diseño global ni otras páginas sin que la persona lo pida.
