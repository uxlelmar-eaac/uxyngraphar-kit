# Mapa de rutas de interfaz

Activado con «usa el paquete paginas-de-interfaz» / «sigue el protocolo paginas» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/paginas-de-interfaz/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Antes de tocar una página, lee su ficha: `python3 $S/comun/fichas.py listar ruta` y `python3 $S/comun/fichas.py ver <id>`.
4. Página nueva: `python3 $S/comun/fichas.py nueva ruta --slug <ruta> --en <modulo> --titulo "/checkout"`.
5. Al cambiar ruta, acceso, datos, estados o componentes principales, actualiza la ficha en la misma tarea. Página eliminada: `fichas.py estado <id> retirada`.
6. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-rutas.py`.

Trabajo: `uxyngraphar/trabajo/paginas-de-interfaz/<modulo>/`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Una ficha por ruta de interfaz** (`path`), incluidas rutas dinámicas (`/orders/[id]`). No hay dos fichas activas con la misma ruta.
2. **`tipo`:** `pagina`, `layout`, `modal-ruta` o `api-interna` (manejadores de ruta del framework).
3. **Acceso explícito:** `auth` (`public`, `sesion`, `rol`) y `roles` si aplica; redirecciones documentadas.
4. **Estados de UI completos:** carga, vacío, error y éxito; cada uno dice qué ve el usuario.
5. **Datos:** qué endpoints o fuentes consume y cuándo (servidor, cliente, caché).
6. **Ficha viva:** un cambio de navegación, acceso, datos o estados actualiza la ficha en la misma tarea.
7. **No borrar fichas:** ruta eliminada → `retirada`; en desuso → `deprecada` con la alternativa.
