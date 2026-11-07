# Componentes

Las piezas que define el paquete. El trabajo vive en `uxyngraphar/trabajo/instrucciones-aprobadas/`.

## Instrucción

Ficha `INS-<AAAAMMDD>-<slug>` en `instrucciones/<estado>/`: el contrato de una tarea (objetivo, alcance, plan, anclas, criterios y lo que queda fuera). Sus status y carpetas:

| Status | Carpeta | Quién lo pone |
|--------|---------|---------------|
| `awaiting_approval` | `pendientes` | al crearla |
| `approved` | `en-progreso` | solo una persona, con `ciclo.py aprobar <id> --humano` (comprueba el alcance y pone `approved_at`) |
| `done` | `completadas` | `ciclo.py cerrar <id>` (pone `executed_at`) |
| `archived` | `archivadas` | `fichas.py estado` |
| `cancelled` | `canceladas` | la persona, con `fichas.py estado` |
| `para-eliminar` | `para-eliminar` | `fichas.py estado` |

## Variante de instrucción

Plantilla alternativa al crearla (`--variante`): `compacta` (cambio pequeño: objetivo, alcance y criterios), `solo-docs` (sin código; los archivos a escribir van en `documentos`) y `adopcion` (primera vez en un repo, por fases de escaneo a comprobación). Sin variante, la plantilla completa con «Clarificación», «Plan» y «Fuera de alcance».

## Clarificación

Sección «Clarificación» y campo `preguntas_id` de la instrucción: las decisiones que la persona tomó antes de redactarla. Si está instalado `preguntas-de-clarificacion`, `preguntas_id` cita su ficha `PRE-…` (en `uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/`) y «Clarificación» copia su síntesis; si no, «Clarificación» recoge lo decidido en el chat o `Omitida (motivo)` y `preguntas_id` queda en `null`.

## Anclas de código

Lista `anclas_codigo` de la instrucción: `ruta` o `ruta:inicio-fin`, relativas a la raíz de la app. Son los únicos archivos que se pueden editar y lo único de código que `ciclo.py contexto` imprime (sin rango, las primeras 200 líneas). Cuentan como archivos de código las extensiones de programa y estilo (`.py`, `.ts`, `.tsx`, `.css`, `.sql`…).

## Lectura mínima

Lista `lectura_minima`: documentos que el agente necesita leer (guías, fichas de otros paquetes). Máximo `max_docs`.

## Presupuesto

Ajustes que acotan una tarea, en `ajustes.json` del trabajo (los fija la persona):

| Ajuste | Por defecto | Qué limita |
|--------|-------------|------------|
| `max_archivos_codigo` | 5 | archivos de código en `anclas_codigo` |
| `max_docs` | 8 | documentos en `lectura_minima` |
| `ampliacion_factor_max` | 2.0 | tope de `ampliacion_factor` |
| `max_tokens_contexto` | 12000 | lo que imprime `contexto`; el resto sale como `OMITIDO` |

## Ampliación

`ampliacion_factor` (entre 1.5 y `ampliacion_factor_max`) con `ampliacion_justificacion`: multiplica el máximo de archivos de código de una instrucción. Sin justificación, la instrucción no se aprueba.

## Fracción

Instrucción que es parte de otra (`fraccion_de: <id>`) y que puede depender de que otras estén cerradas antes (`depende_de: [<id>…]`).

## Estado

`ESTADO.md` en la raíz del trabajo: orientación rápida para entrar en una sesión. El bloque entre `<!-- uxyngraphar:estado -->` y `<!-- /uxyngraphar:estado -->` lo regenera `ciclo.py`; las «Notas» de debajo son de la persona.
