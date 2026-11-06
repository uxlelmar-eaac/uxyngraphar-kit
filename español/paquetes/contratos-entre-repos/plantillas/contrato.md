---
id: {{id}}
status: {{status}}
fecha: {{fecha}}
id_compartido: modulo.recurso.accion
rol: consumidor
method: GET
path: /ejemplo
version: v1
proveedor: nombre-del-repo-que-lo-sirve
ficha_proveedor: null
consumidores: []
---
<!-- id_compartido: el mismo en todos los repos (kebab-case con puntos). rol: proveedor | consumidor | bff (manejador propio del cliente).
     ficha_proveedor: URL o ruta de la ficha de la ruta en el repo proveedor (obligatoria para un consumidor vigente).
     No copies aquí la ficha del proveedor: cítala. -->

# {{titulo}}

## Para qué se usa
Qué pantalla, servicio o flujo depende de este contrato.

## Forma (resumen)
- Entrada: …
- Salida: … (tipos generados desde OpenAPI si existe: dónde)

## Cambios incompatibles
Qué rompería a los consumidores y cómo se versiona (nueva `version`, periodo de convivencia, `deprecado`).
