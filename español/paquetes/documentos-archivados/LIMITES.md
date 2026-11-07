# Límites

Se cumplen en todo el trabajo del paquete.

1. **El archivo no lo lee el agente, nunca.** `archivo/` está fuera de su alcance (`.cursorignore` y equivalentes) y solo la persona lo consulta (`archivo.py buscar … --humano`).
2. **El archivo es histórico e inmutable:** nada en `archivo/` se edita ni se borra; solo se añade.
3. **Archivar es una acción de la persona** (`archivo.py archivar … --humano`); el agente no copia nada a `archivo/`.
4. **El original se borra solo después de archivar**, y solo si la persona lo pide y confirma que la copia existe.
5. **Sin secretos ni datos personales** en lo que se archiva.

## Cuándo detenerse y preguntar

- El pedido exige saber algo que solo está en el archivo: pide a la persona que lo consulte y, si sigue importando, que lo traiga como nota (`notas-de-memoria`).
- La ruta a archivar está bajo `uxyngraphar/paquetes/` o no existe.
- Ese mismo nombre ya se archivó hoy: pregunta si hay que renombrar el original antes.
