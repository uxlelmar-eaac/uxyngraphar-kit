# Caso: página de historial de pedidos

## Pedido

«Crea la página `/account/orders` donde el cliente ve sus pedidos. Solo con sesión.» Módulo `account`, framework con enrutado por carpetas (`src/app/…/page.tsx`).

## Recorrido

**consultar-ficha.** `fichas.py listar pagina` no muestra ninguna ficha con `path: /account/orders`. Sí existe `PAG-20260201-account` (layout `/account`, `auth: sesion`, redirige a `/login`).

**documentar-cambio → documentar-pagina** (skill):

```
python3 $P/scripts/comun/fichas.py nueva pagina --slug account-orders --en account --titulo "/account/orders"
```

Frontmatter: `path: /account/orders`, `tipo: pagina`, `auth: sesion`, `roles: []`, `module: account`.

```markdown
## Acceso
- Requisitos: sesión iniciada (la hereda del layout `/account`).
- Redirecciones: sin sesión → `/login?next=/account/orders`.

## Datos
| Fuente | Cuándo | Para qué |
|--------|--------|----------|
| `GET /orders?page=` | cliente, caché 60 s | lista paginada (ficha RUT-20260115-get-orders) |
```

**completar-estados-de-interfaz** (skill). El código tiene esqueleto de carga, mensaje sin pedidos y tabla; el `catch` del hook solo hace `console.error`, así que el error deja la tabla vacía:

```markdown
## Estados de UI
- Carga: esqueleto de tabla con 5 filas.
- Vacío: «Aún no tienes pedidos» y botón «Ir a la tienda».
- Error: sin resolver (hoy se ve como vacío).
- Éxito: tabla con fecha, total y estado; 20 por página.
```

Se pregunta a la persona; responde que se añada un aviso con «Reintentar». Tras implementarlo: «Error: aviso “No pudimos cargar tus pedidos” con botón “Reintentar”».

**verificar.**

```
$ python3 $P/scripts/verificar-paginas.py
rutas: 2 documentadas, 0 errores, 0 avisos
```

## Resultado

- Ficha `PAG-…-account-orders` con acceso heredado del layout, una fuente de datos enlazada a su ficha de API y los cuatro estados.
- Un estado que el código no resolvía, detectado y decidido por la persona en lugar de inventado.
