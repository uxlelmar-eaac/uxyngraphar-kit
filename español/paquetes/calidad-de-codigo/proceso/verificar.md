---
fase: verificar
resuelve: [archivos-demasiado-largos, nombres-poco-explicativos]
skills: [revisar-calidad, dividir-archivo]
---

# Fase: verificar

## Objetivo

Demostrar que el cambio no introduce problemas nuevos y dejar a la vista los heredados que se vieron.

## Entradas

- Los archivos tocados.
- La lista de problemas heredados de `diagnosticar`.

## Pasos

1. Aplica la skill `revisar-calidad` sobre los archivos tocados (incluidos los nuevos que nacieron al dividir).
2. Compara con la lista de `diagnosticar`: todo problema nuevo es tuyo. Un archivo que creciste por encima del límite vuelve a `dividir-archivo`; un nombre de archivo con espacios se corrige.
3. Los heredados que no pidió la persona no se tocan: si está instalado `deuda-y-mejoras`, regístralos allí; si no, menciónalos al cerrar.
4. Ejecuta las verificaciones del paquete: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/calidad.py <archivos tocados>`.

## Criterio de salida

- `calidad.py` sobre los archivos tocados sale con código 0, o solo informa de problemas heredados que ya figuraban en `diagnosticar`.
- `verificar.py` sin errores.
