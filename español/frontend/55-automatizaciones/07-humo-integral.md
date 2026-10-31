---
id: auto.07.humo-integral
stack: [cliente]
---

# 07: humo-integral

## Fuente

`50-sistema-integral/mapa-capas.md` (capas y su enlace entre repos).

## Valida

Que un cambio no rompió la cadena completa BD → backend → frontend.

## Procedimiento

1. Leer el mapa de capas y resolver el flujo crítico documentado.
2. Ejecutar la ruta crítica de punta a punta en ambiente de prueba.
3. Verificar respuesta y persistencia esperadas.

## Aceptación

- [ ] El flujo crítico documentado completa sin errores.
- [ ] La persistencia resultante coincide con lo documentado.

## Salida

`flujo | pasa / falla | paso donde rompió | evidencia`.
