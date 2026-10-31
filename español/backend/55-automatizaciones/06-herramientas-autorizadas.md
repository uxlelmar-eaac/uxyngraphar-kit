---
id: auto.06.herramientas-autorizadas
stack: [servidor]
---

# 06: herramientas-autorizadas

## Fuente

`35-herramientas/autorizadas/` (registro de lo aprobado por humano).

## Valida

Que todo lo que corre en `automatizaciones/` del proyecto está catalogado
y autorizado. Nada ejecuta sin registro.

## Procedimiento

1. Listar ejecutables en `<proyecto>/automatizaciones/`.
2. Verificar que cada uno tiene ficha en `35-herramientas/autorizadas/`.

## Aceptación

- [ ] Cero ejecutables sin ficha de autorización.
- [ ] Cero fichas autorizadas cuyo ejecutable ya no existe.

## Salida

Dos listas: `sin ficha` y `fichas huérfanas`.
