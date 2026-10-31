# Monorepo — documentación fusionada (opcional)

> **Default:** repos aislados ([sync-multi-repo.md](sync-multi-repo.md)). Esta guía aplica cuando backend y frontend comparten **un solo árbol** y un solo `docs/`.

## Árbol `docs/` único

```
docs/
├── AGENTES.md              # unificado (secciones servidor + cliente)
├── PROTOCOLO.md            # taxonomía común
├── 00-nucleo/
├── 05-instrucciones/
├── 15-rutas/               # API + BFF en subcarpetas por área
├── 25-areas/               # áreas backend y frontend
├── 35-herramientas/
├── 50-sistema-integral/
│   ├── src/                # espejo backend
│   └── apps/web/           # espejo frontend (ejemplo)
└── ...
```

## AGENTES unificado

Un solo `AGENTES.md` en raíz del monorepo con secciones:

- **Común:** presupuesto, instrucciones, herramientas, ciclo vinculante
- **Backend:** anclas `src/modules/`, fichas API
- **Frontend:** anclas UI, refs id sin duplicar ficha

## Espejo dual

Bajo `50-sistema-integral/`:

- Ramas espejo para cada raíz configurada en `configuracion-proyecto.md`
- Un `mapa-capas.md` con filas backend ↔ frontend ↔ id

## Registro ids

Un solo [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md) con el **esquema único** de columnas; «ficha servidor» y «ref externa» pasan a ser paths relativos dentro del monorepo.

## Adopción desde packs separados

1. Fusionar contenido de packs backend + frontend en un `docs/`.
2. Resolver duplicados en `00-nucleo/` (una config, dos secciones stack).
3. Instrucción [_PLANTILLA-adopcion-inicial-pack.md](../05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md) adaptada a monorepo.
4. Revisar [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md) — fila monorepo.

## Referencias

- [configuracion-proyecto.md](../00-nucleo/configuracion-proyecto.md) — `rol: monorepo`
- [sync-multi-repo.md](sync-multi-repo.md) — cuando vuelvan a split repos
- Gap pack monorepo → `46-evolucion-documentacion/` si falta guía/proceso
