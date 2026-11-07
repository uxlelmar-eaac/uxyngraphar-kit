---
name: documentar-pagina
description: Crea la ficha PAG de una página, layout, modal con ruta o manejador de ruta nuevo o sin documentar, con su acceso, sus datos, sus estados y sus archivos ancla.
resuelve: [paginas-sin-ficha, acceso-a-pagina-implicito]
---

# Documentar página

## Cuándo usarla

- Se crea una ruta de interfaz nueva (si aún no existe en el código, status `planificada`).
- Se toca una página existente que no tiene ficha.

## Pasos

1. Elige el slug a partir de la ruta, sin barras ni corchetes: `/orders/[id]` → `orders-id`.
2. Crea la ficha en la carpeta del módulo:
   `python3 $P/scripts/comun/fichas.py nueva pagina --slug orders-id --en orders --titulo "/orders/[id]"`
3. Rellena el frontmatter: `path` (con la sintaxis del enrutador), `tipo` (`pagina`, `layout`, `modal-ruta`, `api-interna`), `auth` (`public`, `sesion`, `rol`), `roles`, `module`.
4. Rellena las secciones leyendo el código:
   - «Qué ve y hace el usuario»: dos o tres frases.
   - «Acceso»: requisitos y a dónde redirige si no se cumplen.
   - «Datos»: una fila por endpoint o fuente, con cuándo se carga (servidor, cliente, caché) y para qué; cita la ficha de `rutas-de-api` si existe.
   - «Estados de UI»: con la skill `completar-estados-de-interfaz`.
   - «Componentes principales» y «Archivos ancla» (un archivo por línea, entre comillas invertidas).
5. Si la ruta aún no existe: `python3 $P/scripts/comun/fichas.py estado <id> planificada`.

## Resultado

- Una ficha `PAG-<fecha>-<slug>.md` en `uxyngraphar/trabajo/paginas-de-interfaz/<modulo>/` con los campos obligatorios y anclas existentes.
