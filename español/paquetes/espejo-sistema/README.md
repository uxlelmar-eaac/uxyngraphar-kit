# Espejo del sistema

Activado con «usa el paquete espejo-sistema» / «sigue el protocolo espejo» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/espejo-sistema/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Para entender código, lee primero su espejo: `python3 $S/espejo.py ver <ruta-del-codigo>`. Mapa y cobertura: `python3 $S/espejo.py mapa [--faltantes]`.
4. Al crear, mover o cambiar la responsabilidad de un archivo o carpeta, crea o actualiza su espejo en la misma tarea: `python3 $S/espejo.py nuevo <ruta-del-codigo>`.
5. Al borrar código, borra su espejo (`python3 $S/espejo.py huerfanos` los lista).
6. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-espejo.py`.

Trabajo: `uxyngraphar/trabajo/espejo-sistema/<ruta-del-codigo>.md` (archivo) y `…/<carpeta>/README.md` (carpeta).

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Ruta espejo:** `src/orders/service.ts` → `uxyngraphar/trabajo/espejo-sistema/src/orders/service.md`; la carpeta `src/orders/` → `…/espejo-sistema/src/orders/README.md`.
2. **Qué se espeja:** archivos con lógica relevante y toda carpeta de módulo. No hace falta espejar pruebas, tipos triviales ni código generado.
3. **Contenido, no copia:** rol, responsabilidades, interacciones y puntos de extensión. Nunca pegues el código.
4. **Espejo vivo:** cambio de responsabilidad, interacciones o ubicación → espejo actualizado en la misma tarea.
5. **Sin huérfanos:** un espejo cuyo código ya no existe es un error; se borra o se mueve con el código.
6. **Tamaño:** indica las líneas del archivo espejado; si supera el límite del proyecto, anótalo.
