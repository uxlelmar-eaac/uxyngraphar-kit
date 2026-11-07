---
name: redactar-propuesta
description: Crea y rellena una ficha PRO con el problema, la solución, las anclas y el alcance que debería permitir un procedimiento repetido, para que una persona decida si lo autoriza.
resuelve: [procedimientos-repetidos-sin-atajo, propuestas-ejecutadas]
---

# Redactar propuesta

## Cuándo usarla

- En `proponer-herramienta`.

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva propuesta --slug <slug> --titulo "…"`. Nace en `propuestas/pendientes/` con `status: pending` y `source: ai`.
2. `motivo`: por qué se propone, con la repetición observada («pedido 4 veces en octubre»).
3. «Problema que resuelve»: la tarea repetida y lo que cuesta hoy hacerla con una instrucción completa.
4. «Solución propuesta»: los comandos exactos o el script que ya existe en el repo; sin pegar código largo. Si hace falta escribir un script nuevo, dilo: eso es trabajo aparte.
5. «Anclas propuestas»: los archivos que la herramienta leería o tocaría, con su ruta.
6. «Alcance que debería permitir»: qué pedidos podrían usarla sin instrucción nueva y cuáles no.
7. «Riesgos»: qué puede salir mal y cómo se detecta.

## Resultado

- Ficha `PRO-<fecha>-<slug>` completa, con el aviso «No ejecutar hasta que una persona la promueva a autorizada».
