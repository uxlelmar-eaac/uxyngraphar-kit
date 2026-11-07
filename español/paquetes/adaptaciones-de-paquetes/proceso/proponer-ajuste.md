---
fase: proponer-ajuste
resuelve: [paquetes-sin-adaptar-al-proyecto, ajustes-locales-desfasados]
skills: [proponer-ajuste-local, revisar-ajustes-desfasados]
---

# Fase: proponer ajuste

Solo si el pedido es crear, revisar o retirar un ajuste local, o si un paso de un paquete activo no encaja. Si no, esta fase no se recorre.

## Objetivo

Dejar la propuesta escrita y lista para que una persona la decida, sin que el agente active ni retire nada.

## Entradas

- El paquete y el archivo de ese paquete que no encaja, con el texto que debería mandar en este proyecto.
- Los ajustes «por revisar» que dejó `consultar-ajustes` o `verificar`.

## Pasos

1. Paso de otro paquete que no encaja → skill `proponer-ajuste-local`.
2. Ajuste «por revisar» o «sin paquete» → skill `revisar-ajustes-desfasados`.
3. Si el cambio vale para todos los proyectos, propón también una EVO en `evolucion-del-sistema` y cítala en `evo`.
4. Ejecuta `python3 $P/scripts/verificar-adaptaciones.py`: la ficha nueva no debe dar avisos.
5. Di a la persona exactamente qué comando decide (sección «Lo que decide la persona» del README).

## Criterio de salida

- La ficha existe en estado `propuesto` sin avisos de `verificar-adaptaciones.py`, o la persona sabe qué ajustes «por revisar» debe revisar o retirar y con qué comando.
