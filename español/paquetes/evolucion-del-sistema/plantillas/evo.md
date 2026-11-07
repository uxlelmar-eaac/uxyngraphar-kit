---
id: {{id}}
status: {{status}}
fecha: {{fecha}}
tipo: proceso
paquete: null
prioridad: despues
detectada_en: null
ajuste_local: null
exportada: null
---
<!-- tipo: cobertura | proceso | plantilla | paquete-nuevo | herramienta. paquete: id del paquete afectado (null = sistema).
     prioridad: ahora | pronto | despues. ajuste_local: AJL-… si se aplica ya en este proyecto (adaptaciones-de-paquetes).
     exportada: fecha en que se exportó para llevarla al catálogo (la escribe evolucion.py exportar). -->

# {{titulo}}

## Qué falta en el sistema
Qué paquete, plantilla o proceso no cubre este caso. Del **sistema**, no del producto.

## Evidencia
Dónde se notó: tarea, instrucción, archivo (`ruta:línea`) o pasos.

## Propuesta
Qué cambiaría en el paquete (archivo y sentido del cambio), sin aplicarlo.

## Decisión a tomar
- Aprobar → se lleva al catálogo (y, si urge, un ajuste local mientras llega).
- Posponer → sigue `pending`.
- Rechazar → `rejected` con el motivo.
