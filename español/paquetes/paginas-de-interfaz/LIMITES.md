# Límites

Se cumplen en todo el trabajo del paquete.

1. **Una ficha por ruta de interfaz** (`path`), incluidas rutas dinámicas (`/orders/[id]`). No hay dos fichas activas con la misma ruta.
2. **`tipo`:** `pagina`, `layout`, `modal-ruta` o `api-interna` (manejadores de ruta del framework).
3. **Acceso explícito:** `auth` (`public`, `sesion`, `rol`) y `roles` si aplica; redirecciones documentadas.
4. **Estados de UI completos:** carga, vacío, error y éxito; cada uno dice qué ve el usuario.
5. **Datos:** qué endpoints o fuentes consume y cuándo (servidor, cliente, caché).
6. **Ficha viva:** un cambio de navegación, acceso, datos o estados actualiza la ficha en la misma tarea.
7. **No borrar fichas:** ruta eliminada → `retirada`; en desuso → `deprecada` con la alternativa.

## Cuándo detenerse y preguntar

- El pedido no dice qué ve el usuario en carga, vacío o error y el código tampoco lo resuelve.
- La página no tiene guarda de acceso en el código y el pedido no dice si es pública.
- Hay dos fichas activas para la misma ruta y no está claro cuál es la buena.
- El pedido es rediseñar o evaluar la experiencia: eso es de `evaluaciones-de-usabilidad` (de `pautas-de-accesibilidad` o `componentes-de-interfaz` si es solo accesibilidad o solo consistencia visual).
