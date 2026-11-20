# Memorias

{{Una frase: qué conviene que el agente y la persona recuerden de este proyecto cuando trabajan con este sistema.}}

Las memorias del proyecto viven en `uxyngraphar/trabajo/<id>/memorias/` y se gestionan con
`python3 uxyngraphar/sistemas-de-gobernanza/<id>/scripts/comun/memorias.py`. El agente las lee al activar el sistema,
aplica las vigentes y propone nuevas (`nueva`, quedan «propuesta»); solo una persona las aprueba o archiva (`--humano`).

## Qué recordar

- {{dato del proyecto que este sistema necesita y que se pierde entre conversaciones}}
- {{decisión de la persona que el agente debe respetar en adelante}}
- {{convención propia del proyecto que el sistema no puede adivinar}}

## Qué no recordar

- {{lo que ya vive en otra parte (fichas, código, otros sistemas) o caduca enseguida}}
- {{lo que se lee del código o del repositorio en cada pedido}}
