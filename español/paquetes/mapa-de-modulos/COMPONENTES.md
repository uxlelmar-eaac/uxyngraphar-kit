# Componentes

Las piezas que define el paquete.

## Área

Parte funcional del sistema con un propósito propio (pedidos, pagos, catálogo). Suele corresponder a uno o varios módulos del código, pero se define por lo que posee, no por las carpetas. Su nombre es el de su carpeta en el trabajo (`uxyngraphar/trabajo/mapa-de-modulos/payments/`).

## Contexto de área

La ficha `ARE-…` del área (plantilla `plantillas/area.md`). Frontmatter: `status` (`active`, `planned`, `deprecated`), `owners` y `depends_on`. Secciones: «Propósito», «Fronteras», «Mapa de lectura», «Código ancla» y «Flujos críticos».

## Fronteras

Cuatro líneas que delimitan el área: **Posee** (datos, endpoints, reglas de negocio de las que es dueña), **No posee** (lo que se confunde con ella y es de otra área), **Escribe en datos** (tablas, colecciones, colas) y **Habla con externos** (servicios de terceros). Dos áreas no poseen lo mismo.

## Dependencia

Entrada de `depends_on`: el nombre de otra área (su carpeta) cuyo código o datos esta necesita. El grafo de dependencias no tiene ciclos; `verificar-areas.py` falla si los hay y avisa si una dependencia apunta a un área sin contexto.

## Mapa de lectura

Lista ordenada de como máximo cinco pasos: lo mínimo que hay que leer para cambiar el área con seguridad. El primero es siempre el propio contexto.

## Código ancla

Carpetas o archivos reales donde empieza el código del área (raíz del módulo, punto de entrada). Si se mueven, el contexto se actualiza.
