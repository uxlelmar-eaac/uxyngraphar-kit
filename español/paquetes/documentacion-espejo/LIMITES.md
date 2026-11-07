# Límites

Se cumplen en todo el trabajo del paquete.

1. **Ruta espejo:** `src/orders/service.ts` → `uxyngraphar/trabajo/documentacion-espejo/src/orders/service.md`; la carpeta `src/orders/` → `…/documentacion-espejo/src/orders/README.md`.
2. **Qué se espeja:** archivos con lógica relevante y toda carpeta de módulo. No hace falta espejar pruebas, tipos triviales ni código generado.
3. **Contenido, no copia:** rol, responsabilidades, interacciones y puntos de extensión. Nunca pegues el código.
4. **Espejo vivo:** cambio de responsabilidad, interacciones o ubicación → espejo actualizado en la misma tarea.
5. **Sin huérfanos:** un espejo cuyo código ya no existe es un error; se borra o se mueve con el código.
6. **Tamaño:** indica las líneas del archivo espejado; si supera el límite del proyecto, anótalo.
7. **No cambies los ajustes** (`raices`, `extensiones`, `excluir`, `cobertura_minima`): son de la persona.

## Cuándo detenerse y preguntar

- El pedido implica espejar decenas de archivos de golpe (adopción en un proyecto existente): propón un orden por módulos.
- `espejo.py huerfanos` lista espejos que no tocaste y el pedido no los incluye.
- No sabes si un archivo tiene lógica relevante (utilidades pequeñas, configuración).
- La cobertura queda por debajo de `cobertura_minima` por código ajeno al pedido.
