# Sync documental en proyectos multi-repo

Guía para PRs que cruzan **repositorio backend** y **repositorio frontend** separados.

## Principio

- **Fuente de verdad API:** `15-rutas/` en repo **servidor**.
- **Cliente:** refs por **id** en [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md) y CONTEXTO.
- **Espejo:** cada repo mantiene su `50-sistema-integral/`; alinear `mapa-capas.md` en ambos si la feature es transversal.

## Orden de merge recomendado

```mermaid
flowchart LR
  PRb[PR backend] --> MergeB[Merge servidor]
  MergeB --> Reg[Actualizar registro ids]
  Reg --> PRf[PR frontend]
  PRf --> MergeF[Merge cliente]
```

1. **Backend primero:** ficha `15-rutas/` + id estable + registro en servidor.
2. **Comunicar id** al equipo frontend (PR description, Slack, issue).
3. **Frontend:** CONTEXTO + registro cliente con ref URL al backend; espejo UI citando id.
4. **Nunca** inventar ids en cliente antes de existir en servidor (salvo acuerdo explícito en instrucción coordinada).

## Checklist PR backend

- [ ] Ficha `15-rutas/<area>/<id>.md` con frontmatter `id`
- [ ] Fila en [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md)
- [ ] CONTEXTO área actualizado
- [ ] Espejo API en `50-sistema-integral/` si aplica
- [ ] `mapa-capas.md` — fila feature ↔ repo cliente

## Checklist PR frontend (después)

- [ ] Registro cliente: ref URL a ficha servidor
- [ ] CONTEXTO UI: consumo del **id** (no copia de ficha)
- [ ] Espejo UI + `mapa-capas.md`
- [ ] BFF nuevo → ficha local `15-rutas/` solo si aplica

## Instrucción coordinada (opcional)

Para features grandes: una instrucción en **cada** repo con el mismo título lógico y enlace cruzado en Resultado. Presupuesto ampliado con aprobación humana.

## Monorepo

Si backend+frontend comparten árbol, usar [monorepo-docs-fusionados.md](monorepo-docs-fusionados.md) en lugar de este flujo.

## Referencias

- [sync-documentacion-pr.md](sync-documentacion-pr.md)
- [configuracion-proyecto.md](../00-nucleo/configuracion-proyecto.md)
