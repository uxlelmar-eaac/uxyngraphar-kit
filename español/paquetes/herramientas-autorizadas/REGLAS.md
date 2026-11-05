# Herramientas autorizadas — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **El agente nunca crea, edita ni revoca fichas en `autorizadas/`.** Solo una persona autoriza (`authorized`) o revoca (`revoked`).
2. **Ejecutar solo dentro del alcance:** si el pedido no encaja exactamente en «Alcance permitido», no uses la herramienta; sigue el proceso normal.
3. **Solo ficha y anclas:** al ejecutar una herramienta lees su ficha y sus `anclas_codigo`, nada más.
4. **Las propuestas no se ejecutan.** Una propuesta `pending` es una sugerencia hasta que una persona la promueva.
5. **Toda autorizada declara** `authorized_by`, `authorized_at`, alcance, riesgos y anclas existentes.
6. **Revocada = inexistente:** una herramienta `revoked` no se usa aunque encaje.
