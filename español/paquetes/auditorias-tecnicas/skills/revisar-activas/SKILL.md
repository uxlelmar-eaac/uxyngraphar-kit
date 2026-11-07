---
name: revisar-activas
description: Lista las auditorías activas y pendientes, detecta las que superan max_activas o llevan más de dias_sin_cambios sin avanzar y propone cerrarlas o posponerlas.
resuelve: [auditorias-abandonadas]
---

# Revisar activas

## Cuándo usarla

- Antes de abrir una auditoría (fase `abrir-auditoria`).
- Cuando `verificar-auditorias.py` avisa de demasiadas activas o de una activa sin cambios.
- Cuando la persona pregunta en qué estado están las auditorías.

## Pasos

1. Lista las activas: `python3 $P/scripts/comun/fichas.py listar auditoria --status activa`; y las pospuestas: `… --status pendiente`.
2. Ejecuta `python3 $P/scripts/verificar-auditorias.py`: los avisos «activa sin cambios hace N días» y «N auditorías activas (máximo M)» señalan las que hay que tratar.
3. Para cada activa estancada, propone a la persona cerrarla con lo que haya (fase `concluir`) o pasarla a `pendiente`: `python3 $P/scripts/comun/fichas.py estado AUD-… pendiente`.
4. No cierres ni pospongas una auditoría ajena al pedido sin que la persona lo diga.

## Resultado

- Lista de activas y pendientes con su antigüedad, y una propuesta para cada una estancada.
