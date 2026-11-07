---
fase: implementar
resuelve: [secretos-en-el-codigo, archivos-de-secretos-versionados]
skills: [sustituir-por-variable-de-entorno, marcar-dato-de-prueba]
---

# Fase: implementar

## Objetivo

Hacer el cambio pedido sin escribir ni leer ningún valor sensible.

## Entradas

- Las variables de entorno decididas en `diagnosticar`.

## Pasos

1. Todo valor sensible que el código necesite se lee de una variable de entorno o se escribe como `<PLACEHOLDER>`: aplica la skill `sustituir-por-variable-de-entorno`.
2. No abras, imprimas, copies ni generes archivos de secretos (`.env`, `*.pem`, `credentials.json`…). Si el pedido los menciona, trabaja sobre `.env.example` y explica a la persona qué valores pone ella.
3. En pruebas, usa valores evidentemente falsos (`example`, `dummy`, `changeme`). Si un formato concreto obliga a algo realista, aplica la skill `marcar-dato-de-prueba` (requiere permiso de la persona).
4. Nada de secretos en fichas, commits, logs ni en la respuesta: si hay que nombrar uno, ruta + línea + muestra enmascarada.

## Criterio de salida

- Ningún valor sensible real en lo que escribiste y ningún archivo de secretos creado o leído.
