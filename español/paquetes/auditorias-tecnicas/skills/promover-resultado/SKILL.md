---
name: promover-resultado
description: Crea en el paquete destino la ficha de una promoción aceptada (ADR, instrucción, mejora o documentación) citando la auditoría, y la anota en «promociones» de la ficha AUD.
resuelve: [conclusiones-sin-seguimiento]
---

# Promover resultado

## Cuándo usarla

- En la fase `promover`, por cada promoción que la persona aceptó.

## Pasos

1. Comprueba que el paquete destino está instalado (`uxyngraphar/paquetes/<destino>/`). Si no lo está, di a la persona qué ficha habría que crear y dónde, y no la inventes en otro sitio.
2. Crea la ficha con el `fichas.py` del destino, desde la raíz de la app:
   - ADR: `python3 uxyngraphar/paquetes/decisiones-de-arquitectura/scripts/comun/fichas.py nueva adr --slug <slug> --titulo "…"`
   - mejora: `python3 uxyngraphar/paquetes/deuda-y-mejoras/scripts/comun/fichas.py nueva mejora --slug <slug> --titulo "…"`
   - instrucción: según el proceso de `instrucciones-aprobadas` (su README).
3. En la ficha nueva, cita la auditoría (`AUD-…`) y copia la evidencia de los hallazgos que la justifican.
4. Añade el id de la ficha creada a `promociones` del frontmatter de la auditoría (`promociones: [ADR-20261106-indice-pedidos]`) y actualiza `actualizado`.

## Resultado

- La ficha en el paquete destino, enlazada desde la auditoría y la auditoría desde ella.
