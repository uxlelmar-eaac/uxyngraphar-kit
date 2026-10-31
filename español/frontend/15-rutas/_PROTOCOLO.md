# Protocolo de rutas (cliente)

Solo se documentan aquí **manejadores de ruta / BFF propios** de este repo (`app/api/**`, `routes/api/**`). Rutas del API backend: **no** crear ficha; citar su `id` en [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md).

## Nomenclatura de ficha

```
15-rutas/<módulo>/<método>-<path-slug>.md
```

Ejemplo: `dashboard/get-widgets.md`.

## Obligatorio en cada ficha

1. **Hace** — propósito en 1–3 frases.
2. **Entrada / salida** — cuerpo, query, cabeceras relevantes; forma de respuesta (sin OpenAPI completo).
3. **Conectado con** — hooks/casos de uso, integraciones, ids del API consumidos.
4. **Pipeline** — manejador de ruta → `api/` → `reception/` → `hooks/` según aplique.
5. **Archivos ancla** — rutas concretas en el código.

## Id estable (frontmatter)

```yaml
id: modulo.accion.nombre
status: activa
```

Prefijo distinto al del servidor si comparten nombre semántico. Estados: `activa` | `deprecated`.

## Sincronización

Manejador nuevo o cambiado → ficha + fila en [INDICE.md](INDICE.md) + índice del CONTEXTO del área, en el mismo PR.
