# Componentes

Las piezas que define el paquete. El trabajo vive en `uxyngraphar/trabajo/herramientas-autorizadas/`.

## Herramienta autorizada

Ficha `HER-<AAAAMMDD>-<slug>` en `autorizadas/` (cualquier subcarpeta): un procedimiento que una persona autorizó para ejecutarse sin instrucción nueva cuando el pedido encaja en su alcance. Declara qué hace, cuándo usarla y cuándo no, cómo ejecutarla, su «Alcance permitido», sus riesgos y sus `anclas_codigo`. Tipo plano con dos status, ambos solo de una persona:

| Status | Significado |
|--------|-------------|
| `authorized` | vigente: se puede usar si el pedido encaja |
| `revoked` | retirada: como si no existiera |

La crea la persona con `fichas.py nueva autorizada --slug <slug> --humano` y debe tener `source: human`, `authorized_by` y `authorized_at`.

## Propuesta

Ficha `PRO-<AAAAMMDD>-<slug>` en `propuestas/<estado>/`: un procedimiento que el agente sugiere autorizar. Nace con `source: ai` y no se ejecuta.

| Status | Carpeta | Quién lo pone |
|--------|---------|---------------|
| `pending` | `pendientes` | al crearla |
| `en-evaluacion` | `en-progreso` | el agente, cuando está completa |
| `promovida` | `completadas` | solo una persona, al crear la autorizada correspondiente |
| `rejected` | `canceladas` | solo una persona |
| `archivada` | `archivadas` | cuando deja de tener sentido |
| `para-eliminar` | `para-eliminar` | creada por error |

`pending` y `en-evaluacion` esperan a una persona: `revision-humana` las recoge.

## Alcance permitido

Sección de la herramienta que enumera los pedidos que habilitan usarla sin instrucción nueva. Es una lista cerrada: lo que no está, no está autorizado.

## Anclas de código

`anclas_codigo` de la herramienta: los archivos que lee o toca (`ruta` o `ruta:inicio-fin`). Al ejecutarla no se lee nada más; `verificar-herramientas.py` avisa si alguna no existe.

## Promoción

Paso de propuesta a herramienta: la persona crea la ficha `HER-…` a partir de la propuesta (con `authorized_by` y su alcance definitivo) y pone la propuesta en `promovida`.
