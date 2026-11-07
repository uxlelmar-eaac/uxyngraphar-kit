# Adaptaciones de paquetes

Permite que una persona adapte un archivo de un paquete instalado a este proyecto sin editarlo: el ajuste local manda sobre ese archivo solo aquí, se imprime al activar el paquete y queda «por revisar» en cuanto el archivo cambia.

## Qué resuelve

Los paquetes instalados son inmutables: se reemplazan enteros al actualizar y su integridad falla si alguien los toca. Cuando un paso no encaja en este proyecto (un comando que aquí no existe, otra carpeta, otro idioma para los commits), hoy solo queda editarlo a mano o ignorarlo en silencio. Este paquete da un tercer camino: un ajuste local (`AJL-…`) que una persona aprueba, que el agente sigue por encima del texto original cada vez que activa ese paquete y que guarda la huella del archivo para avisar cuando el paquete cambia y el ajuste puede haberse quedado viejo.

## Problemas que cubre

- `paquetes-sin-adaptar-al-proyecto`: un paquete inmutable con un paso o una regla que no encaja en este proyecto.
- `ajustes-locales-desfasados`: ajustes locales que siguen mandando sobre un archivo de paquete que cambió desde su aprobación.

## Fuera de alcance

- Reglas propias del equipo para su código y sus excepciones: `reglas-del-proyecto`.
- Cambiar un paquete del catálogo para todos los proyectos: `evolucion-del-sistema` (el ajuste local es el puente mientras tanto).
- Valores de configuración que un paquete ya expone en `uxyngraphar/trabajo/<id>/ajustes.json`: los edita la persona directamente; no hace falta un ajuste local.
- Instalar, actualizar o reparar la integridad de un paquete: lo hace el motor de uxyngraphar, no un paquete.

## Cuándo usarlo

- Al activar cualquier paquete instalado: el agente ejecuta `adaptaciones.py ajustes <id>` (`al_activar_paquete`) y sigue lo que imprima.
- Cuando un paso de otro paquete instalado no encaja en este proyecto.
- Cuando la persona quiere probar un cambio de un paquete antes de llevarlo al catálogo.
- Después de actualizar paquetes, para revisar los ajustes que quedaron «por revisar».

## Cuándo no usarlo

- Si el cambio vale para todos los proyectos y no urge: propón directamente una EVO en `evolucion-del-sistema`.
- Para fijar una convención del código del proyecto: eso es una regla de `reglas-del-proyecto`.

## Entradas y salidas

- Entradas: las fichas de `uxyngraphar/trabajo/adaptaciones-de-paquetes/ajustes-locales/` y los archivos de `uxyngraphar/paquetes/<id>/` a los que apuntan.
- Salidas: fichas `AJL-…` nuevas en estado `propuesto`; los ajustes activos de un paquete al activarlo (`## AJL-… → manda sobre <id>/<archivo>` y su cuerpo); avisos de `verificar-adaptaciones.py` para los ajustes «por revisar» o cuyo paquete ya no está.

## Paquetes complementarios

- `evolucion-del-sistema`: la ficha EVO que lleva al catálogo lo que hoy es un ajuste local (se cita en el campo `evo`).
- `reglas-del-proyecto`: si está instalado, `adaptaciones.py ajustes` lee su carpeta de trabajo y recuerda cuántas reglas activas hay para pasar por `reglas.py para <rutas>` antes de tocar código.
- `revision-humana`: recoge los ajustes `propuesto` que esperan a una persona.
