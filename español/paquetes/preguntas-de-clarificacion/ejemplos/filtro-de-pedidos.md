# Caso: decidir el filtro del listado de pedidos antes de redactarlo

## Pedido

«Añade al listado de pedidos un filtro por estado.» Ajustes por defecto (`preguntas: true`, `dias_en_curso: 7`). El proyecto tiene instalado también `instrucciones-aprobadas`, que redactará la instrucción.

## Recorrido

**preguntar.** Lo que cambia el resultado y el código no responde: dónde vive el filtro y qué estados se ofrecen. Que el listado use `findAll` del servicio se lee en el código; no se pregunta. En el chat:

1. ¿El filtro va en la URL (`?estado=pagado`, recomendado: se puede compartir) o solo en memoria? → URL.
2. ¿Todos los estados o solo `pendiente`, `pagado`, `enviado`? → los tres.

Skill `registrar-pregunta`:

```
python3 $P/scripts/comun/fichas.py nueva pregunta --slug filtro-pedidos --titulo "Filtro de pedidos por estado"
uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/en-curso/PRE-20261106-filtro-pedidos.md
```

La ficha queda así:

```markdown
## Impacto
Dónde vive el filtro y qué estados se ofrecen: cambia la URL pública del listado y qué ve el usuario.

## Decisiones
| # | Pregunta | Opciones | Elegida | Efecto |
|---|----------|----------|---------|--------|
| 1 | ¿Filtro en la URL o en memoria? | URL (recomendada) · memoria | URL | se lee de `?estado=` en el controlador |
| 2 | ¿Qué estados? | todos · pendiente, pagado, enviado | los tres | lista fija en el servicio |

## Síntesis
- Filtro en la URL; estados pendiente, pagado y enviado.
```

**cerrar-pregunta.** Siguiendo su propio proceso, `instrucciones-aprobadas` crea `INS-20261106-filtro-pedidos`, copia la síntesis en «Clarificación» y pone `preguntas_id: PRE-20261106-filtro-pedidos`. Aquí, skill `enlazar-pregunta`: `instruccion_id: INS-20261106-filtro-pedidos` en la pregunta y

```
python3 $P/scripts/comun/fichas.py estado PRE-20261106-filtro-pedidos completada
uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/completadas/PRE-20261106-filtro-pedidos.md
python3 $P/scripts/verificar-preguntas.py
preguntas-de-clarificacion: 0 errores, 0 avisos
```

## Resultado

- Las dos decisiones las tomó la persona; ninguna quedó a criterio del agente.
- `PRE-20261106-filtro-pedidos` está en `completadas/`, enlazada en ambos sentidos con la instrucción.

## Variantes

- **Se cierra sin responder.** Si el agente cerrara la ficha recién creada, sin rellenar, `verificar-preguntas.py` termina con código 1:

  ```
  error: uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/completadas/PRE-20261106-filtro-pedidos.md: decisión 1 sin pregunta
  error: uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/completadas/PRE-20261106-filtro-pedidos.md: síntesis vacía
  preguntas-de-clarificacion: 2 errores, 0 avisos
  ```

  Y si la persona no hubiera contestado la segunda pregunta y el agente dejara «Elegida» en `…`: `decisión 2 sin «Elegida» de la persona`.
- **Sin `instrucciones-aprobadas`.** La síntesis se da en el chat antes de cambiar nada, `instruccion_id` queda en `null` y la verificación no busca ninguna instrucción.
- **«Salta preguntas».** No se crea ficha; se avisa a la persona y la instrucción lleva `Omitida (pedido)` en «Clarificación».
