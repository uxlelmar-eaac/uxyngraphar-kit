---
fase: verificar
resuelve: [dependencias-entre-areas-circulares, dependencias-hacia-areas-sin-documentar]
skills: [revisar-dependencias-entre-areas]
---

# Fase: verificar

## Objetivo

Demostrar que el grafo de dependencias entre áreas sigue sin ciclos y que las anclas citadas existen.

## Entradas

- Los contextos creados o tocados.

## Pasos

1. Aplica la skill `revisar-dependencias-entre-areas`.
2. Comprueba a mano que cada ruta de «Código ancla» de los contextos tocados existe (el script no lo revisa).
3. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- `verificar-areas.py` termina con código 0 (sin ciclos).
- Sin avisos de dependencias sin documentar introducidos por la tarea.
- Anclas de los contextos tocados existentes.
