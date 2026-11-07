# Límites

Se cumplen en todo el trabajo del paquete.

1. **El agente nunca crea, edita ni revoca fichas en `autorizadas/`.** Solo una persona autoriza (`authorized`) o revoca (`revoked`).
2. **Ejecutar solo dentro del alcance:** si el pedido no encaja exactamente en «Alcance permitido», no uses la herramienta; sigue el proceso normal.
3. **Solo ficha y anclas:** al ejecutar una herramienta lees su ficha y sus `anclas_codigo`, nada más.
4. **Las propuestas no se ejecutan.** Una propuesta `pending` es una sugerencia hasta que una persona la promueva.
5. **Toda autorizada declara** `authorized_by`, `authorized_at`, alcance, riesgos y anclas existentes.
6. **Revocada = inexistente:** una herramienta `revoked` no se usa aunque encaje.
7. **Tal como está escrita:** los comandos de «Cómo ejecutarla» se ejecutan sin cambiar argumentos ni añadir pasos; si hace falta otra cosa, el pedido ya no encaja.

## Cuándo detenerse y preguntar

- El pedido encaja solo en parte en el «Alcance permitido» de una herramienta.
- Un ancla de la herramienta no existe o `verificar-herramientas.py` da errores en su ficha.
- Al ejecutarla, un comando falla o el resultado no es el que dice «Cómo ejecutarla».
- La herramienta necesitaría tocar archivos que no están en sus anclas.
