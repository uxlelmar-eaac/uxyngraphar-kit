# Protocolo de rutas

## Nomenclatura de ficha

```
15-rutas/<módulo>/<método>-<path-slug>.md
```

Ejemplos: `get-ejemplo-elementos.md`, `post-ejemplo-elementos.md`.

## Obligatorio en cada ficha

1. **Hace** — propósito en 1–3 frases.
2. **Entrada / salida** — cuerpo, query, cabeceras relevantes; forma de respuesta (sin OpenAPI completo).
3. **Conectado con** — casos de uso, integraciones, tablas, eventos externos.
4. **Pipeline por capas** — entrada → aplicación → dominio/infra/integraciones.
5. **Archivos ancla** — rutas concretas en el código.

## Sincronización

- Ruta nueva/cambiada → ficha + fila en este INDICE + índice en `25-areas/<módulo>/CONTEXTO.md`.
- No duplicar el OpenAPI entero; la ficha es el mapa operativo para humanos/IA.

## Id estable (frontmatter)

```yaml
id: modulo.recurso.accion
```

Usar ese `id` en instrucciones, auditorías y CONTEXTO.
