---
fase: documentar-cambio
resuelve: [paginas-sin-ficha, fichas-de-pagina-desfasadas, estados-de-interfaz-sin-definir, acceso-a-pagina-implicito, rutas-de-interfaz-documentadas-dos-veces]
skills: [documentar-pagina, completar-estados-de-interfaz, retirar-pagina]
---

# Fase: documentar-cambio

## Objetivo

Que la ficha refleje la página tal como queda al terminar la tarea, en la misma tarea que cambia el código.

## Entradas

- El resultado de `consultar-ficha`.
- El código de la página tras el cambio: archivo de ruta, guardas o middleware, carga de datos y componentes.

## Pasos

1. Elige la skill según el cambio:
   - página nueva o sin ficha → `documentar-pagina`;
   - la ruta se elimina o se sustituye → `retirar-pagina`;
   - cambia la ruta, el acceso, los datos o los componentes → edita la ficha existente (frontmatter `path`, `auth`, `roles`; secciones «Acceso», «Datos», «Componentes principales», «Archivos ancla») y actualiza `fecha`.
2. Si el cambio toca carga de datos o manejo de errores, aplica `completar-estados-de-interfaz`.
3. Comprueba el acceso contra el código: guarda, middleware o layout que redirige. Las redirecciones van en «Acceso».
4. Revisa que cada archivo de «Archivos ancla» exista con esa ruta exacta.

## Criterio de salida

- La ficha tiene `path`, `tipo`, `auth` (y `roles` si `auth: rol`) acordes al código.
- «Estados de UI» dice qué ve el usuario en carga, vacío, error y éxito.
- El status es el correcto: `activa`, `planificada`, `deprecada` o `retirada`.
