---
name: revisar-idioma
description: Ejecuta idiomas.py sobre unos archivos (o sobre todas las raíces) para detectar nombres de archivo no ASCII y repasa a mano el idioma de identificadores, comentarios, logs y textos del cambio.
resuelve: [codigo-en-idioma-mezclado]
---

# Revisar idioma

## Cuándo usarla

- Al empezar (fase `diagnosticar`) y al terminar (fase `verificar`) un cambio.
- Cuando la persona pide un diagnóstico del idioma de una carpeta o de todo el proyecto.

## Pasos

1. Solo tus archivos: `python3 $P/scripts/idiomas.py <archivo>…`. Todo el proyecto: `python3 $P/scripts/idiomas.py` (recorre `raices` con `extensiones` y sin `excluir`).
2. Cada línea `<archivo>: nombre de archivo no ASCII; tradúcelo al inglés (referencia/idioma.md)` → si el archivo es tuyo, renómbralo en inglés ASCII (y sus imports); si es heredado, anótalo.
3. La última línea resume: `idiomas-del-codigo: <n> archivos revisados, <m> problemas`. Código 0 = sin problemas; 1 = hay problemas.
4. El script no lee el contenido: repasa en esos archivos identificadores, comentarios, logs y errores para desarrolladores. Fuera del inglés ASCII solo valen los términos de `python3 $P/scripts/glosario.py terminos`, los campos de contratos externos en la frontera y los textos de los archivos de locale.
5. En un proyecto que adopta el paquete con mucho código en otro idioma, no lo renombres: resume por carpeta y propón a la persona qué renombrar y en qué tandas.

## Resultado

- Lista de problemas de idioma de los archivos revisados, separados en tuyos y heredados.
