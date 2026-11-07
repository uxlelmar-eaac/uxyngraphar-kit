---
fase: consultar-ficha
resuelve: [paginas-sin-ficha, rutas-de-interfaz-documentadas-dos-veces]
skills: []
---

# Fase: consultar-ficha

## Objetivo

Saber qué está documentado de la página antes de tocarla (acceso, datos, estados), o confirmar que aún no tiene ficha.

## Entradas

- El pedido: qué ruta de interfaz se crea, cambia o elimina.
- Las fichas de `uxyngraphar/trabajo/paginas-de-interfaz/`.

## Pasos

1. Lista las fichas: `python3 $P/scripts/comun/fichas.py listar pagina` (con `--status activa` si hay muchas).
2. Busca la ruta (con su sintaxis dinámica, p. ej. `/orders/[id]`) y ábrela: `python3 $P/scripts/comun/fichas.py ver <id>`.
3. Si hay dos fichas activas para la misma ruta, detente y pregunta cuál es la buena (límite 1).
4. Anota lo que el cambio no debe romper: «Acceso», «Estados de UI» y las fuentes de «Datos».
5. Si no hay ficha, se crea en `documentar-cambio` con la skill `documentar-pagina`.

## Criterio de salida

- Tienes el id de la ficha de la página o sabes que no existe.
- No hay dos fichas activas para la misma ruta.
