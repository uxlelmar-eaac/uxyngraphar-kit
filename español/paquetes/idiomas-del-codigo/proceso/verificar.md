---
fase: verificar
resuelve: [codigo-en-idioma-mezclado]
skills: [revisar-idioma]
---

# Fase: verificar

## Objetivo

Demostrar que el cambio no introduce mezcla de idiomas y dejar a la vista lo heredado y los términos propuestos para el glosario.

## Entradas

- Los archivos tocados.
- La lista de problemas heredados de `diagnosticar`.

## Pasos

1. Aplica la skill `revisar-idioma` sobre los archivos tocados (incluidos los nuevos).
2. Repasa el diff: identificadores, comentarios, logs y textos nuevos en inglés ASCII, salvo términos del glosario; ningún texto para el usuario escrito en la lógica.
3. Compara con la lista de `diagnosticar`: todo problema nuevo es tuyo y se corrige. Lo heredado que no pidió la persona no se toca: si está instalado `deuda-y-mejoras`, regístralo allí; si no, menciónalo al cerrar.
4. Si propusiste términos para el glosario, enuméralos al cerrar con su fila completa para que la persona decida.
5. Ejecuta las verificaciones del paquete: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/idiomas.py <archivos tocados>`.

## Criterio de salida

- `idiomas.py` sobre los archivos tocados sale con código 0, o solo informa de problemas heredados que ya figuraban en `diagnosticar`.
- `verificar.py` sin errores.
