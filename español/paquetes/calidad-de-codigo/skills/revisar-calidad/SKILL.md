---
name: revisar-calidad
description: Ejecuta calidad.py sobre unos archivos (o sobre todas las raíces) y clasifica cada problema en límite de líneas o nombre de archivo con espacios.
resuelve: [archivos-demasiado-largos, nombres-poco-explicativos]
---

# Revisar calidad

## Cuándo usarla

- Al empezar (fase `diagnosticar`) y al terminar (fase `verificar`) un cambio.
- Cuando la persona pide un diagnóstico de calidad de una carpeta o de todo el proyecto.

## Pasos

1. Solo tus archivos: `python3 $P/scripts/calidad.py <archivo>…`. Todo el proyecto: `python3 $P/scripts/calidad.py` (recorre `raices` con `extensiones` y sin `excluir`).
2. Lee cada línea:
   - `<archivo>: <n> líneas (límite <l>); divide por responsabilidad (referencia/limite-lineas.md)` → skill `dividir-archivo` si el crecimiento es tuyo.
   - `<archivo>: nombre de archivo con espacios` → renombra el archivo (y sus imports) si es tuyo, con la skill `elegir-nombres`.
3. La última línea resume: `calidad-de-codigo: <n> archivos revisados, <m> problemas`. Código 0 = sin problemas; 1 = hay problemas.
4. `calidad.py` no juzga si un identificador es genérico: revisa a ojo los nombres nuevos del cambio contra `referencia/nombres.md`.
5. En un proyecto que adopta el paquete con muchos problemas, no los corrijas todos: resume por carpeta y propón tandas a la persona.

## Resultado

- Lista de problemas de los archivos revisados, separados en tuyos y heredados.
