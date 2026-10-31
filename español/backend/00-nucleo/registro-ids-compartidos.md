# Registro de ids compartidos (API ↔ cliente)

> **Repos aislados:** este archivo vive en **cada** repositorio. La columna «ref externa» usa URL o path **externo**, no rutas locales al otro pack.

Fuente de verdad de las fichas HTTP: `15-rutas/` del **repo servidor**. El cliente cita ids; solo los BFF propios tienen ficha local.

## Tabla de ids (esquema único cliente/servidor)

| id | ficha servidor | ficha local (BFF) | área cliente | ref externa | estado | notas |
|----|----------------|-------------------|--------------|-------------|--------|-------|
| `<endpoint-id>` | `docs/15-rutas/...` (repo servidor) | — | `<area-ui>` | `<URL a la ficha>` | activa | Versión API, deprecación |
| `<bff-id>` | — | `docs/15-rutas/...` (solo pack cliente) | `<area>` | — | activa | Handler propio |
| — | — | — | — | — | — | (vacío al adoptar) |

## Reglas

1. **Servidor:** ficha en `15-rutas/` con `id` estable; fila aquí al merge.
2. **Cliente:** citar `id` en CONTEXTO y espejo; **no** duplicar ficha HTTP; BFF propio → ficha local + fila.
3. **PR cruzados:** merge backend primero; alinear esta tabla en ambos repos — [sync-multi-repo.md](../10-guias/sync-multi-repo.md).
4. **Deprecar:** `estado: deprecated` aquí y `status: deprecated` en la ficha; renombrar id solo con instrucción explícita.
5. **Monorepo:** una sola tabla en `docs/` unificado — [monorepo-docs-fusionados.md](../10-guias/monorepo-docs-fusionados.md).

## Referencias

- [configuracion-proyecto.md](configuracion-proyecto.md)
- [15-rutas/INDICE.md](../15-rutas/INDICE.md)
