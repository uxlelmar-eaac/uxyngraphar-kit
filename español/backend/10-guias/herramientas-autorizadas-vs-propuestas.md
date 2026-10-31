# Herramientas autorizadas vs propuestas IA

Cuándo usar cada subcarpeta de [`35-herramientas/`](../35-herramientas/INDICE.md).

## Comparación

| | **autorizadas/** | **propuestas/** |
|---|------------------|-----------------|
| Quién crea | Humano (manual) | IA (vía instrucción) |
| Ejecutar sin instrucción | **Sí** (excepción) | **No** |
| Estado típico | `authorized` | `pending` → humano decide |
| Ejemplos | Script de validación OpenAPI, migración repetitiva | IA sugiere cache, codegen nuevo |

## Flujo autorizada (agilizar)

1. Humano copia [_PLANTILLA-autorizada.md](../35-herramientas/_PLANTILLA-autorizada.md) → `autorizadas/<id>.md`.
2. Rellena alcance permitido, anclas al script en el repo, `authorized_by`.
3. Añade fila en `autorizadas/INDICE.md`.
4. Agente puede ejecutar cuando el pedido humano encaja **sin** instrucción nueva.

## Flujo propuesta (sugerir → decidir)

1. Durante instrucción, IA detecta oportunidad reutilizable.
2. Crea ficha en `propuestas/01-pendientes/YYYY-MM-DD/<slug>.md` (`status: pending`).
3. Registra en `herramientas_propuestas` y Resultado de la instrucción.
4. Humano revisa:
   - **Aprobar** → copiar/adaptar a `autorizadas/` con `source: human`
   - **Rechazar** → mover a `propuestas/05-canceladas/`

## Qué no va aquí

- Procedimientos ops largos → `30-manuales/`
- Onboarding → `10-guias/`
- Cambios de producto → instrucción normal + `25-areas/`

Protocolo: [35-herramientas/_PROTOCOLO.md](../35-herramientas/_PROTOCOLO.md)
