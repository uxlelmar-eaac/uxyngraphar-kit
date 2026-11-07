---
name: componer-mosaico
description: Elige los tamaños de las celdas para que la protagonista sea la mayor, las prioridades sean 1..n y la suma de áreas llene filas completas de la rejilla, y lo comprueba con verificar-bento.py.
resuelve: [mosaico-sin-jerarquia, paginas-sin-objetivo-unico]
---

# Componer mosaico

## Cuándo usarla

- En `disenar-mosaico`, al pasar de la lista de mensajes a la tabla «Mosaico».
- Cuando `verificar-bento.py` informa de huecos, tamaños no permitidos o una protagonista que no es la mayor.

## Pasos

1. Parte de una composición de `referencia/patrones-bento.md`: «protagonista + apoyo» (6 celdas), «banda + mosaico» (5) o «rejilla regular» (8, sin protagonista).
2. Asigna a la prioridad 1 la celda de mayor área (`2x2` o la banda `4x1`); como mucho `max_2x2` celdas `2x2`.
3. Suma áreas (`ancho × alto`): el total debe ser múltiplo de `columnas` (12 = 3 filas de 4). Si da 13 o 14, quita o agranda una celda.
4. Pon el CTA `primario` en una sola celda, la protagonista o la banda; un CTA repetido al final es `secundario`.
5. Escribe la tabla con prioridades 1..n sin repetir y ejecuta `python3 $P/scripts/verificar-bento.py`.

## Resultado

- Tabla «Mosaico» sin avisos de tamaño, prioridad, CTA ni huecos en `verificar-bento.py`.
