# Herramientas autorizadas

Activado con «usa el paquete herramientas-autorizadas» / «sigue el protocolo herramientas» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/herramientas-autorizadas/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. ¿Hay una herramienta autorizada que cubra el pedido? `python3 $S/comun/fichas.py listar autorizada --status authorized`. Si encaja en su «Alcance permitido», ejecútala tal como dice (solo su ficha y sus anclas).
4. Si ves un procedimiento repetido que convendría autorizar, **propónlo**: `python3 $S/comun/fichas.py nueva propuesta --slug <slug>`. No lo ejecutes como herramienta.
5. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-herramientas.py`.

Persona: autorizar = `python3 $S/comun/fichas.py nueva autorizada --slug <slug> --humano` (o promover una propuesta copiándola) y `fichas.py estado <propuesta> promovida --humano`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **El agente nunca crea, edita ni revoca fichas en `autorizadas/`.** Solo una persona autoriza (`authorized`) o revoca (`revoked`).
2. **Ejecutar solo dentro del alcance:** si el pedido no encaja exactamente en «Alcance permitido», no uses la herramienta; sigue el proceso normal.
3. **Solo ficha y anclas:** al ejecutar una herramienta lees su ficha y sus `anclas_codigo`, nada más.
4. **Las propuestas no se ejecutan.** Una propuesta `pending` es una sugerencia hasta que una persona la promueva.
5. **Toda autorizada declara** `authorized_by`, `authorized_at`, alcance, riesgos y anclas existentes.
6. **Revocada = inexistente:** una herramienta `revoked` no se usa aunque encaje.
