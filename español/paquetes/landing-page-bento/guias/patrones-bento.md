# Patrones bento

Un mosaico bento es una rejilla de celdas de tamaños distintos donde **el tamaño comunica importancia**. Funciona cuando cada celda dice una sola cosa y la jerarquía se entiende de un vistazo.

## Composiciones probadas (4 columnas)

- **Protagonista + apoyo (6 celdas):** `2x2` (1) · `2x1` (2) · `1x1` (3) · `1x1` (4) · `2x1` (5) · `2x1` (6) → 4+2+1+1+2+2 = 12 = 3 filas.
- **Banda + mosaico (5 celdas):** `4x1` (1, propuesta de valor y CTA) · `2x2` (2) · `1x2` (3) · `1x1` (4) · `1x1` (5) → 4+4+2+1+1 = 12 = 3 filas. Comprueba siempre la suma: si da 13 o 14, sobra o falta una celda.
- **Rejilla regular (8 celdas):** `2x1` ×4 + `1x1` ×4 = 12. Útil para catálogos de funciones sin protagonista (entonces `max_2x2` no se usa).

## Contenido por celda

- Título: beneficio, no función («Cobra en 2 minutos», no «Módulo de pagos»).
- Mensaje: una prueba o detalle concreto (cifra, ejemplo, testimonio corto).
- Medio: refuerza el mensaje; si es decorativo, `icono` y fuera del árbol de accesibilidad.
- CTA: el primario vive en la protagonista o en una banda `4x1`; repetirlo al final de la página es la misma acción, no un segundo CTA primario distinto.

## Errores frecuentes

- Todas las celdas del mismo tamaño con prioridades distintas: la jerarquía no se ve.
- Texto largo dentro de celdas pequeñas: rompe en móvil.
- Orden móvil por posición visual: la protagonista acaba en tercer lugar.
- Celdas solo decorativas: si no comunica nada, sobra.
