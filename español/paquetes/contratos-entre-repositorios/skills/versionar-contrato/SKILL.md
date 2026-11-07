---
name: versionar-contrato
description: Gestiona un cambio incompatible de un contrato compartido con versión nueva, convivencia de las dos versiones y la anterior marcada como deprecada.
resuelve: [cambios-incompatibles-sin-version, ids-compartidos-inconsistentes]
---

# Versionar contrato

## Cuándo usarla

- El cambio quita o renombra campos, cambia tipos, la ruta o el método, o endurece validaciones que los consumidores no cumplen.
- Se quiere renombrar un `id_compartido`.

## Pasos

1. No edites `method`, `path` ni `version` del contrato actual.
2. Crea un contrato nuevo con la skill `crear-contrato`: mismo `id_compartido` y `version` siguiente (`v2`), o un `id_compartido` nuevo si se renombra.
3. Describe en «Cambios incompatibles» de los dos contratos qué rompe, cuánto dura la convivencia y qué deben cambiar los consumidores.
4. Marca el anterior: `python3 $P/scripts/comun/fichas.py estado <id-anterior> deprecado`.
5. La retirada (`retirado`) la decide una persona cuando ningún consumidor vigente usa la versión anterior; recuérdalo al cerrar.
6. Regenera el registro: `python3 $P/scripts/contratos.py registro`.

## Resultado

- Dos contratos conviviendo: el nuevo `propuesto` y el anterior `deprecado`, con la convivencia explicada.
