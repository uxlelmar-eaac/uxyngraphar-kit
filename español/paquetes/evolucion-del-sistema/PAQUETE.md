# Evolución del sistema

Recoge lo que les falta a los paquetes de uxyngraphar instalados (un caso no cubierto, una plantilla incompleta, un proceso que no encaja) como fichas EVO con evidencia, sin tocar los paquetes, y las prepara para llevarlas al catálogo.

## Qué resuelve

Los paquetes instalados son inmutables y se reemplazan enteros al actualizar. Cuando uno no cubre un caso, hay dos tentaciones: editarlo a mano (rompe la integridad y el cambio se pierde en la siguiente versión) o callarlo (el hueco sigue ahí). Este paquete ofrece un buzón: una EVO por carencia con evidencia y propuesta, una matriz de cobertura que muestra qué dimensiones del proyecto cubren los paquetes instalados, y una exportación anónima que la persona lleva al catálogo. Mientras llega, la persona puede activar un ajuste local en `adaptaciones-de-paquetes`.

## Problemas que cubre

- `carencias-del-sistema-sin-registro`: huecos de paquetes, plantillas o procesos que se pierden.
- `paquetes-editados-en-el-proyecto`: paquetes instalados editados a mano para salir del paso.
- `cobertura-desconocida`: no se sabe qué cubren los paquetes instalados y qué falta.
- `propuestas-sin-llegar-al-catalogo`: EVO aprobadas que no se exportan o con un estado que no refleja la realidad.

## Fuera de alcance

- Deuda técnica y bugs del producto: `deuda-y-mejoras`.
- Investigaciones técnicas del producto: `auditorias-tecnicas`.
- El ajuste local que adapta un paquete a este proyecto mientras llega el cambio: `adaptaciones-de-paquetes`.
- Aplicar el cambio en el catálogo y publicar la versión nueva del paquete: lo hace quien mantiene el catálogo con el motor; no lo cubre ningún paquete.

## Cuándo usarlo

- Cuando, trabajando con un paquete, su proceso, plantilla o verificación no encaja con el caso real.
- Cuando falta un paquete entero para una dimensión del proyecto.
- Al adoptar uxyngraphar en un proyecto, para rellenar la matriz de cobertura.
- Cuando la persona quiere llevar al catálogo las mejoras acumuladas.

## Cuándo no usarlo

- Para problemas del código o del producto: `deuda-y-mejoras`.
- Para cambiar cómo trabaja un paquete solo en este proyecto y de forma permanente: `adaptaciones-de-paquetes`.
- En tareas normales: las EVO no se leen salvo al registrar una o si la persona lo pide.

## Entradas y salidas

- Entradas: la carencia observada y su evidencia (tarea, archivo del paquete, pasos), los paquetes instalados en `uxyngraphar/paquetes/` y los ajustes de `uxyngraphar/trabajo/evolucion-del-sistema/ajustes.json`.
- Salidas: fichas `EVO-…` en `uxyngraphar/trabajo/evolucion-del-sistema/<estado>/`, `MATRIZ-COBERTURA.md` y, por decisión de la persona, informes `exportaciones/EXPORTACION-<fecha>.md` sin rutas absolutas.

## Paquetes complementarios

- `adaptaciones-de-paquetes`: ajuste local que cita la EVO mientras el catálogo no la incorpora.
- `revision-humana`: recoge las EVO `pending` y `approved` que esperan decisión.
- `deuda-y-mejoras`: la cola equivalente para el producto.
