---
fase: consultar-ajustes
resuelve: [paquetes-sin-adaptar-al-proyecto, ajustes-locales-desfasados]
skills: [aplicar-ajustes-locales]
---

# Fase: consultar ajustes

## Objetivo

Saber, antes de trabajar con un paquete, qué partes suyas sustituye este proyecto y si alguna adaptación está «por revisar».

## Entradas

- Los paquetes activos en esta tarea (los nombrados en el pedido y los que fija `uxyngraphar/FLUJO.json`).

## Pasos

1. Para cada paquete activo, aplica la skill `aplicar-ajustes-locales` (el motor ya lo pide al activar un paquete: `adaptaciones.py ajustes <id>`).
2. Anota, por paquete, qué archivo sustituye cada ajuste y cuáles están «por revisar» o «sin paquete».
3. Si el pedido es crear, revisar o retirar un ajuste, salta a `proponer-ajuste`.

## Criterio de salida

- Sabes qué ajustes locales mandan en los paquetes activos (puede no haber ninguno) y cuáles hay que comunicar a la persona.
