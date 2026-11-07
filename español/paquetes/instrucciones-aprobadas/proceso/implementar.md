---
fase: implementar
resuelve: [alcance-desbordado]
skills: [anotar-fuera-de-alcance]
---

# Fase: implementar

## Objetivo

Hacer el cambio aprobado, solo en las anclas, sin arrastrar mejoras ni arreglos que nadie pidió.

## Entradas

- El contexto impreso en `cargar-contexto`.
- El «Plan» y los «Criterios de aceptación» de la instrucción.

## Pasos

1. Sigue el «Plan» de la instrucción en orden.
2. Edita solo archivos de `anclas_codigo` (y, en la variante `solo-docs`, solo los de `documentos`). Respeta los rangos: fuera de `ruta:inicio-fin` solo lo imprescindible para que el cambio compile (un import, una firma).
3. Si necesitas un archivo que no está en las anclas, detente: propón ampliar la instrucción (vuelve a `esperar-aprobacion`) o deja ese trabajo para una instrucción hija.
4. Deuda, bugs o mejoras que veas por el camino: aplica `anotar-fuera-de-alcance`; no los implementes.
5. Marca en la instrucción cada criterio de aceptación a medida que se cumple (`- [x]`).

## Criterio de salida

- Todos los cambios están dentro de las anclas aprobadas.
- Los criterios cumplidos están marcados; lo detectado y no hecho está en «Fuera de alcance».
