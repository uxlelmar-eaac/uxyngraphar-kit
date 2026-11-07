# Componentes

Las piezas que define el paquete. El trabajo vive en `uxyngraphar/trabajo/preguntas-de-clarificacion/`.

## Pregunta

Ficha `PRE-<AAAAMMDD>-<slug>` en `preguntas/<estado>/`: las decisiones que la persona tomó antes de redactar o cambiar nada, con opciones, elegida y efecto. Sus status y carpetas:

| Status | Carpeta | Quién lo pone |
|--------|---------|---------------|
| `en-curso` | `en-curso` | al crearla; mientras se pregunta y se registran las respuestas |
| `completada` | `completadas` | `fichas.py estado <id> completada`, con todas las decisiones elegidas y la síntesis escrita |
| `cancelada` | `canceladas` | `fichas.py estado <id> cancelada`, si el pedido se abandona |

Mientras está `en-curso`, la pregunta espera respuestas de la persona (`revision-humana` la muestra entre las decisiones pendientes).

## Decisión

Fila de la tabla «Decisiones»: `#`, «Pregunta», «Opciones» (con la recomendada marcada), «Elegida» (lo que respondió la persona) y «Efecto» en el trabajo. Una fila sin «Elegida» es una decisión sin tomar: la pregunta no se puede cerrar.

## Síntesis

Sección «Síntesis»: las decisiones en viñetas, listas para copiar en «Clarificación» de una instrucción o en el plan del cambio.

## Enlace con la instrucción

Campo `instruccion_id` de la pregunta: la instrucción de `instrucciones-aprobadas` que usa su síntesis (que a su vez la cita en `preguntas_id`). Queda en `null` si el paquete no está instalado o la síntesis se usa en otro trabajo.

## Ajustes

En `ajustes.json` del trabajo (los fija la persona):

| Ajuste | Por defecto | Qué controla |
|--------|-------------|--------------|
| `preguntas` | `true` | si la fase `preguntar` se hace |
| `dias_en_curso` | 7 | días que una pregunta puede seguir `en-curso` antes de que `verificar-preguntas.py` avise |
