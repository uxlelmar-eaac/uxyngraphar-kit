---
id: auto.09.limite-lineas
stack: [cliente]
---

# 09: limite-lineas

## Fuente

Protocolo de líneas del proyecto (defecto: **350 líneas** por archivo
de código; excluye generados, snapshots y vendored).

## Valida

Que ningún archivo de código excede el tope. Archivo largo = señal de
que pide partición.

## Procedimiento

1. Contar líneas de cada archivo de código (respetar exclusiones del
   protocolo del proyecto).
2. Reportar los que exceden, con conteo exacto.

## Aceptación

- [ ] Cero archivos por encima del tope sin excepción documentada.
- [ ] Cada excepción tiene su justificación registrada (decisión activa
  en `20-decisiones/`).

## Salida

Lista: `archivo | líneas | exceso | excepción (sí/no)`.
