---
name: dividir-archivo
description: Divide un archivo que pasa de limite_lineas en archivos hermanos por responsabilidad, con nombre relacional, dejando el original como fachada.
resuelve: [archivos-demasiado-largos]
---

# Dividir archivo

## Cuándo usarla

- `calidad.py` informa que un archivo que tú hiciste crecer supera `limite_lineas`.
- Vas a añadir a un archivo cercano al límite algo que lo haría pasar.

No la uses en archivos que ya excedían el límite y que el pedido no toca: avísalos.

## Pasos

1. Lista las responsabilidades del archivo (validación, cálculo, acceso a datos, presentación, tipos) y qué funciones pertenecen a cada una.
2. Extrae cada responsabilidad a un archivo hermano: nombre original + sufijo de la responsabilidad, con la convención de archivos del lenguaje (`order-service.ts` → `order-service.pricing.ts`; `user_service.py` → `user_service_queries.py`).
3. Deja el original como fachada: compone y reexporta lo que sus importadores usaban; no duplica lógica. Así ningún importador externo cambia.
4. Mueve las pruebas junto a la parte que prueban.
5. Ejecuta `python3 $P/scripts/calidad.py <original> <hermanos>` y las pruebas del proyecto.
6. Nunca dividas por número de líneas (`parte1`, `parte2`) ni comprimas código para esquivar el límite; nunca pidas tú una exención.

## Resultado

- El original y sus hermanos por debajo del límite, con los mismos exports públicos que antes.
