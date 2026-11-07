# Caso: filtrar el listado de pedidos por estado

## Pedido

«Añade al listado de pedidos un filtro por estado.» Ajustes por defecto (máximo 5 archivos de código). El proyecto tiene instalado también `preguntas-de-clarificacion`, que ya dejó la ficha `PRE-20261106-filtro-pedidos` con la síntesis «Filtro en la URL; estados pendiente, pagado y enviado» (su recorrido está en los ejemplos de ese paquete).

## Recorrido

**redactar-instruccion.** Lo que cambia el resultado ya está decidido por la persona; no se supone nada más.

```
python3 $P/scripts/comun/fichas.py nueva instruccion --slug filtro-pedidos --titulo "Filtrar pedidos por estado"
uxyngraphar/trabajo/instrucciones-aprobadas/instrucciones/pendientes/INS-20261106-filtro-pedidos.md
```

Frontmatter relevante:

```yaml
preguntas_id: PRE-20261106-filtro-pedidos
anclas_codigo:
  - src/orders/orders.service.ts:40-52
  - src/orders/orders.controller.ts:10-18
```

La síntesis de la pregunta se copia en «Clarificación». Dos archivos de código, dentro del máximo. Sin `preguntas-de-clarificacion` instalado, «Clarificación» recogería las dos decisiones tomadas en el chat y `preguntas_id` quedaría en `null`. Mientras esperaba, el agente vio que `orders.service.ts` no pagina; lo deja en «Fuera de alcance» (skill `anotar-fuera-de-alcance`).

**esperar-aprobacion.** Resumen para la persona: «2 archivos; el filtro se lee de `?estado=` en el controlador y se aplica en `findAll` del servicio; la paginación queda fuera». Si el agente intentara aprobar:

```
python3 $P/scripts/ciclo.py aprobar INS-20261106-filtro-pedidos
error: «approved» solo lo asigna una persona (usa --humano si eres tú)
```

y `contexto` responde con código 3:

```
BLOQUEADO: la instrucción está en «awaiting_approval»; necesita aprobación de una persona.
```

La persona aprueba desde su terminal con `ciclo.py aprobar INS-20261106-filtro-pedidos --humano`; la ficha pasa a `en-progreso/` con `approved_at`.

**cargar-contexto.** `ciclo.py contexto INS-20261106-filtro-pedidos` imprime la ficha y solo los rangos aprobados:

```
===== src/orders/orders.service.ts:40-52 =====
   40| async findAll(): Promise<Order[]> {
   …
===== src/orders/orders.controller.ts:10-18 =====
   10| @Get()
   …
~1450 tokens de 12000
```

**implementar.** Se añade el parámetro `estado` al controlador y el `where` en `findAll`, sin salir de esos rangos salvo el import del tipo del estado. Los dos criterios de aceptación quedan marcados.

**cerrar.**

```
python3 $P/scripts/ciclo.py cerrar INS-20261106-filtro-pedidos
uxyngraphar/trabajo/instrucciones-aprobadas/instrucciones/completadas/INS-20261106-filtro-pedidos.md
python3 $P/scripts/verificar-ciclo.py
instrucciones-aprobadas: 0 errores, 0 avisos
```

`ESTADO.md` muestra «Última cerrada | INS-20261106-filtro-pedidos — Filtrar pedidos por estado» y sus tokens de contexto.

## Resultado

- Dos archivos cambiados, ambos en las anclas aprobadas.
- Las decisiones de la persona quedan citadas en `preguntas_id`; la paginación, anotada para otra instrucción.

## Variante: el pedido no cabe

Si el filtro exigiera tocar 7 archivos, `ciclo.py aprobar … --humano` respondería `no se puede aprobar: 7 archivos de código en anclas (máximo 5); fracciona o justifica una ampliación`. El agente aplica `fraccionar-instruccion` (servidor en una instrucción, cliente en otra con `depende_de`) o, si no se puede partir, `justificar-ampliacion` con `ampliacion_factor: 1.5`.
