---
fase: ejecutar-herramienta
resuelve: [procedimientos-repetidos-sin-atajo, herramientas-usadas-fuera-de-alcance, autorizaciones-sin-responsable]
skills: []
---

# Fase: ejecutar-herramienta

## Objetivo

Hacer lo que la herramienta autoriza, exactamente como está escrito, sin leer ni tocar nada fuera de su ficha y sus anclas.

## Entradas

- La ficha `HER-…` elegida en `buscar-herramienta`.

## Pasos

1. Ejecuta `python3 $P/scripts/verificar-herramientas.py`. Si da errores en esta ficha (sin `authorized_by`, sin `authorized_at`, `source` distinto de `human`), no la uses: avisa a la persona.
2. Lee la ficha (`python3 $P/scripts/comun/fichas.py ver <HER-…>`): «Cómo ejecutarla», «Riesgos y límites» y `anclas_codigo`.
3. Ejecuta los comandos de «Cómo ejecutarla» en orden, sin cambiar argumentos. Comprueba tras cada uno que el resultado es el esperado.
4. Si un comando falla o el resultado no coincide, detente: no improvises un arreglo. Informa a la persona.
5. Si la herramienta modifica archivos, comprueba que todos están en `anclas_codigo`.
6. Informa a la persona: qué herramienta usaste (id), qué comandos y qué cambió.

## Criterio de salida

- Los comandos se ejecutaron tal como dice la ficha y con el resultado esperado, o el fallo está informado sin arreglos improvisados.
- Ningún archivo fuera de las anclas cambió.
