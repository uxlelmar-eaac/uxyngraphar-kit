# Bloques de decisión machine-readable (R-16)

El bloque **Decisión a tomar** declara que la decisión **sigue abierta** y
que **su efecto no está aplicado**. Emitir una ficha con bloque cuando el
cambio ya está hecho deja al revisor sin saber si debe decidir o enterarse.

| Tipo de ficha | Decisión ya tomada (humano) | Decisión abierta |
|---|---|---|
| Instrucción `05-instrucciones/` | `status: approved` (o `done`) + `approved_at` · **sin** bloque | `awaiting_approval` · **con** bloque |
| ADR `20-decisiones/` | `status: aceptada` · **sin** bloque | `propuesta` · **con** bloque |
| Mejora `45-mejoras-propuestas/` | `status: approved` + `instruction_derivada` · **sin** bloque | `pending` · **con** bloque |
| Evolución `46-evolucion-documentacion/` | `status: approved`/`done` + `instruction_derivada` · **sin** bloque | `pending` · **con** bloque |
| Auditoría `40-auditorias/` — promociones | promoción ejecutada y citada · **sin** bloque | `activa` (`02-en-progreso`) · **con** bloque |

Cada estado emitido lleva además su carpeta de estado (R-17).

Reglas:

1. **Sin bloque ⇒ sección `Aprobación`.** Toda ficha en estado final dice
   **quién** decidió, **cuándo** y **dónde**. Sin trazabilidad, la ficha
   vuelve a pendiente.
2. **Prohibido «efecto aplicado + decisión pendiente».** O el efecto no
   está aplicado (ficha pendiente), o está aplicado porque se aprobó
   (estado final). Al cerrar: ratificar o revertir **antes**.
3. **La duda va a pendiente.** Sin aprobación explícita, ficha pendiente y
   **código intacto** (R-03).
4. Las plantillas traen el bloque por defecto; **suprimirlo** en estado
   final es aplicar esta regla, no modificar la plantilla (R-14).

## Formato del bloque

En fichas con decisión humana pendiente, sección **Decisión a tomar**
(alias retrocompatible: **Decisión humana**).

```markdown
## Decisión a tomar

<!-- decision-group: <id-frontmatter> -->
- [ ] <!-- decision:aprobar --> **Aprobar** → …
- [ ] <!-- decision:posponer --> **Posponer** — …
- [ ] <!-- decision:rechazar --> **Rechazar** → …
```

| Regla | Detalle |
|-------|---------|
| `decision-group` | Coincide con `id` del frontmatter, o `{id}-suffix` |
| Alias sección | **Decisión humana** — el scanner usa `id` si no hay comentario |
| `decision:<accion>` | Id único dentro del grupo (`aprobar`, `rechazar`, `promover`, …) |
| Checklists operativos | **No** usar `decision-group` en guías (`10-guias/`) salvo decisión real |
| Revisión de pendientes | [`decisiones-pendientes`](../../35-herramientas/autorizadas/decisiones-pendientes.md) — CLI |

Acciones por tipo: instrucción (`awaiting_approval`): `aprobar`, `cancelar`;
mejora (`pending`): `aprobar`, `posponer`, `rechazar`; herramienta
(`pending`): `promover`, `rechazar`.
