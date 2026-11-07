# Componentes

Las piezas que define el paquete.

## Memoria

`uxyngraphar/trabajo/notas-de-memoria/memoria/`: carpeta de notas. El agente puede escribir en ella cuando la persona pide conservar algo, pero solo la lee a través de `notas.py buscar` y solo cuando el pedido lo pide expresamente. No forma parte del contexto por defecto de ningún pedido.

## Nota

Ficha `MEM-…` de la memoria (plantilla `plantillas/nota.md`). Frontmatter: `fuente` (conversación, incidente, decisión: de dónde sale), `valida_hasta` (fecha o condición a partir de la cual deja de valer; `null` si no caduca) y `status` (`vigente` o `archivada`). Secciones: «Qué hay que recordar» y «Por qué importa».

## Nota archivada

Archivar una nota es solo cambiar su `status` a `archivada` (con la causa escrita en la propia nota). Sigue en `memoria/` y sale en las búsquedas, pero no se usa como cierta. No tiene nada que ver con el archivo histórico de documentos (`documentos-archivados`).
