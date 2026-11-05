# Espejo del sistema — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Ruta espejo:** `src/orders/service.ts` → `uxyngraphar-work/espejo-sistema/src/orders/service.md`; la carpeta `src/orders/` → `…/espejo-sistema/src/orders/README.md`.
2. **Qué se espeja:** archivos con lógica relevante y toda carpeta de módulo. No hace falta espejar pruebas, tipos triviales ni código generado.
3. **Contenido, no copia:** rol, responsabilidades, interacciones y puntos de extensión. Nunca pegues el código.
4. **Espejo vivo:** cambio de responsabilidad, interacciones o ubicación → espejo actualizado en la misma tarea.
5. **Sin huérfanos:** un espejo cuyo código ya no existe es un error; se borra o se mueve con el código.
6. **Tamaño:** indica las líneas del archivo espejado; si supera el límite del proyecto, anótalo.
