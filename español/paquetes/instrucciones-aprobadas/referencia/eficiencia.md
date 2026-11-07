# Eficiencia: leer lo mínimo

La instrucción aprobada es el contrato de lectura: lo que no está en `lectura_minima`, `anclas_codigo` o lo que imprime `ciclo.py contexto` no se abre.

## Presupuesto por tarea (por defecto)

| Recurso | Máximo |
|---------|--------|
| Instrucción | 1 (la de la tarea) |
| Documentos (`lectura_minima`) | `max_docs` (8) |
| Archivos de código (`anclas_codigo`) | `max_archivos_codigo` (5); ampliable ×1.5–2 con justificación y aprobación |
| Contexto impreso | `max_tokens_contexto` (12000); lo que no cabe sale como «OMITIDO» |
| `ESTADO.md` | 1, opcional, al entrar |
| Colas de otros paquetes (mejoras, propuestas, archivo) | 0, salvo que la tarea sea revisarlas |

Ampliar el presupuesto = editar la instrucción y volver a pedir aprobación.

## Qué leer según la tarea

| Tarea | Lee | No lee |
|-------|-----|--------|
| Implementar | `ciclo.py contexto <id>` | el resto del repo |
| Solo documentación (variante `solo-docs`) | `lectura_minima` y los `documentos` | código |
| Investigar un fallo | contexto + la auditoría activa que lo trate | colas de mejoras |
| Pregunta de solo lectura | el área nombrada (1 ficha) | historial, archivo |
| Adopción (variante `adopcion`) | la fase en curso | las demás fases |

## Hábitos

- **No reabrir** en la misma sesión un archivo ya leído, salvo que haya cambiado en disco.
- **Rangos en las anclas** (`ruta:inicio-fin`): sin rango, `contexto` imprime solo las primeras 200 líneas.
- **Costo visible:** `contexto` anota `tokens_contexto` en la instrucción y `ESTADO.md` lo muestra para las últimas cerradas; si sube mucho, la instrucción era demasiado grande: fracciona la siguiente.
