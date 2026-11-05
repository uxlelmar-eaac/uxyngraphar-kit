# Mapa de rutas de interfaz — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Una ficha por ruta de interfaz** (`path`), incluidas rutas dinámicas (`/orders/[id]`). No hay dos fichas activas con la misma ruta.
2. **`tipo`:** `pagina`, `layout`, `modal-ruta` o `api-interna` (manejadores de ruta del framework).
3. **Acceso explícito:** `auth` (`public`, `sesion`, `rol`) y `roles` si aplica; redirecciones documentadas.
4. **Estados de UI completos:** carga, vacío, error y éxito; cada uno dice qué ve el usuario.
5. **Datos:** qué endpoints o fuentes consume y cuándo (servidor, cliente, caché).
6. **Ficha viva:** un cambio de navegación, acceso, datos o estados actualiza la ficha en la misma tarea.
7. **No borrar fichas:** ruta eliminada → `retirada`; en desuso → `deprecada` con la alternativa.
