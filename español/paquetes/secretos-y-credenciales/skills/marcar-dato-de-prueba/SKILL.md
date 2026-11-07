---
name: marcar-dato-de-prueba
description: Exime del escaneo una línea de datos de prueba ficticios con la marca uxyngraphar:permitir-secreto, solo con permiso de la persona y sin tocar los ajustes.
resuelve: [escaneo-silenciado]
---

# Marcar dato de prueba

## Cuándo usarla

- Una prueba necesita un valor con el formato exacto de una credencial (por ejemplo, para probar el propio detector o un validador de formato) y `secretos.py` lo marca.
- Nunca para valores reales ni para que el escaneo pase con prisa.

## Pasos

1. Intenta primero un valor evidentemente falso que el escáner ya ignora (`example`, `dummy`, `changeme`, `<…>`) o construir el valor en tiempo de ejecución (`"AKIA" + "EXAMPLE…"`).
2. Si no basta, pide permiso a la persona indicando ruta, línea y por qué el valor ficticio necesita ese formato.
3. Con permiso, añade la marca en un comentario de la misma línea: `const fakeKey = "…"; // uxyngraphar:permitir-secreto`.
4. No añadas la ruta a `permitir` ni a `excluir` en `ajustes.json`: son de la persona y eximen archivos enteros.
5. Vuelve a escanear: la línea marcada ya no sale; cualquier otra del archivo sí.

## Resultado

- Solo esa línea queda exenta, con permiso explícito, y el resto del archivo sigue escaneándose.
