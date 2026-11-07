---
name: retirar-endpoint
description: Marca la ficha de un endpoint eliminado como retirada o la de uno en desuso como deprecada con su alternativa, sin borrarla.
resuelve: [endpoints-retirados-sin-rastro, rutas-documentadas-dos-veces]
---

# Retirar endpoint

## Cuándo usarla

- Se elimina un endpoint del código.
- Un endpoint sigue respondiendo pero ya no se recomienda (lo sustituye otro).
- Un cambio incompatible crea un endpoint nuevo que convive con el anterior.

## Pasos

1. Localiza la ficha: `python3 $P/scripts/comun/fichas.py listar ruta --status activa`.
2. Endpoint en desuso: añade en «Hace» la alternativa (método, ruta y su ficha) y desde cuándo; luego `python3 $P/scripts/comun/fichas.py estado <id> deprecada`.
3. Endpoint eliminado: anota en «Hace» en qué cambio se eliminó y `python3 $P/scripts/comun/fichas.py estado <id> retirada`.
4. No borres el archivo de la ficha ni sus secciones: los clientes antiguos y las auditorías la consultan.
5. Las anclas de una ficha retirada pueden dejar de existir; los avisos de `verificar-rutas.py` sobre ellas se mencionan, no se corrigen.

## Resultado

- La ficha sigue en su carpeta con status `deprecada` (y alternativa) o `retirada`, y no cuenta como duplicada frente a la nueva.
