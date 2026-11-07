---
name: comprobar-encaje-de-pedido
description: Decide si un pedido cabe entero en el «Alcance permitido» de una herramienta autorizada vigente, comparándolo frase a frase con su ficha.
resuelve: [herramientas-usadas-fuera-de-alcance]
---

# Comprobar encaje de pedido

## Cuándo usarla

- En `buscar-herramienta`, con cada herramienta candidata.
- Cuando la persona pide expresamente «usa la herramienta X»: también hay que comprobar que el pedido encaja.

## Pasos

1. Comprueba que la ficha tiene `status: authorized`. Si es `revoked`, no encaja, aunque el resto coincida.
2. Lee «Alcance permitido» y «Cuándo usarla», incluido el «No usar si: …».
3. Compara el pedido con cada condición: qué se pide, sobre qué archivos o datos, con qué parámetros. Debe cumplirlas todas.
4. Si el pedido añade algo (otro entorno, otro módulo, un paso extra), no encaja: la parte extra no está autorizada.
5. Si encaja solo en parte, detente y pregunta a la persona si quiere limitar el pedido a lo autorizado o seguir el proceso normal.

## Resultado

- «Encaja» (con la herramienta y la condición del alcance que lo permite), «no encaja» (con lo que sobra) o «encaja en parte» (pregunta a la persona).
