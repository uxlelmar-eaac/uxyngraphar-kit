# Componentes

Las piezas que define el paquete. Su único archivo de trabajo es `uxyngraphar/trabajo/revision-humana/REVISION.md`.

## Pendiente

Una ficha de cualquier paquete instalado cuyo status está entre los que esperan a una persona. Se identifica por paquete e id, y lleva su status, los días que lleva esperando, su título, las opciones y el comando de cada una.

## Status que esperan

Lo declara cada paquete en su manifiesto, por tipo de ficha: `espera_humano` (por ejemplo, ADR en `propuesta` o `en-evaluacion`) o, si no lo declara y el tipo tiene `solo_humano`, su status `inicial` (por ejemplo, instrucciones en `awaiting_approval`). Un tipo sin `solo_humano` ni `espera_humano` nunca aparece.

## Opciones

Los status que la persona puede poner a un pendiente: los `solo_humano` de su tipo (`approved` en una instrucción; `aceptada` o `rechazada` en una ADR). Además, en la hoja vale `posponer` o dejar la decisión vacía.

## Comando de decisión

Cómo se aplica cada opción. Si el paquete declara `comandos` para ese status, se usa ese (`approved` → `scripts/ciclo.py aprobar {id} --humano`); si no, `scripts/comun/fichas.py estado {id} <status> --humano` del paquete dueño. Así cada decisión pasa por las comprobaciones de su paquete.

## Hoja de revisión

`REVISION.md`: tabla `| Paquete | Ficha | Status | Días | Título | Opciones | Decisión |` generada por `revision.py preparar`. Está en `protegidos`: la IA no la edita; la persona escribe la columna «Decisión» y `aplicar` la regenera al terminar con lo que sigue pendiente.

## Antigüedad

Días desde el campo `actualizado` o `fecha` de la ficha (o, si no tiene, desde su última modificación). Por encima de `dias_aviso` (14 por defecto, ajustable en `ajustes.json`), la ficha se señala como antigua.
