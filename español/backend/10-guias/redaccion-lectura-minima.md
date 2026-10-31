# Redacción de `lectura_minima` — guía humana (servidor)

Cómo declarar la **lista cerrada** de docs que la IA puede abrir en una tarea backend. Canon tokens: [eficiencia-ia.md](../00-nucleo/eficiencia-ia.md).

## Regla de oro

> Si un path no está en `lectura_minima` (ni en el mapa del CONTEXTO citado), **la IA no debe abrirlo**.

## Cuántos paths incluir

| Tipo | Máximo recomendado |
|------|-------------------|
| `CONTEXTO.md` del área | 1 (obligatorio si hay `areas`) |
| Fichas `15-rutas/` | 1–2 |
| ADR / auditoría activa | 0–1 |
| **Total `lectura_minima`** | **≤3** (presupuesto global default: 8 docs en total, incluye `AGENTES.md` + instrucción) |

`espejo_leer`: casi siempre `[]`. Si se usa, máx. 3 paths y cuentan contra `presupuesto_max_docs`.

## Qué incluir

- `docs/25-areas/<area>/CONTEXTO.md` del dominio afectado
- Fichas HTTP citadas en el plan
- ADR o auditoría **solo** si la tarea depende de ellas

## Qué no incluir

- `docs/INDICE.md`, `docs/PROTOCOLO.md`
- `docs/10-guias/` (salvo acto `adoptar` con instrucción explícita)
- Índices de carpetas (`*/INDICE.md`)
- `docs/90-archivo/`
- Colas `45-mejoras-propuestas/` o `46-evolucion-documentacion/` (salvo revisión de pendientes)
- Espejo `50-sistema-integral/` (salvo consulta previa en `espejo_leer`)

## Ejemplo mínimo (endpoint nuevo)

```yaml
lectura_minima:
  - docs/25-areas/pedidos/CONTEXTO.md
  - docs/15-rutas/pedidos/post-pedido.md
espejo_leer: []
presupuesto_max_docs: 8
```

## Ampliar presupuesto

Si la tarea requiere más docs: subir `presupuesto_max_docs` en frontmatter **y** obtener aprobación humana explícita en la sección **Decisión a tomar**.

## Referencias

- [flujo-instrucciones-documentacion.md](flujo-instrucciones-documentacion.md)
- [convenciones-frontmatter.md](../00-nucleo/convenciones-frontmatter.md)
