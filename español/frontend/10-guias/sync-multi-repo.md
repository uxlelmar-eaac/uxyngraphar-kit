# Sync documental en proyectos multi-repo (cliente)

Perspectiva **frontend** cuando el backend vive en otro repositorio.

## Reglas

1. **No duplicar** fichas HTTP del servidor en `15-rutas/` del cliente.
2. Consumir API por **id** documentado en el repo backend.
3. Actualizar [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md) con **URL** a la ficha servidor (GitHub, GitLab, etc.).
4. Esperar merge backend antes de cerrar PR frontend que dependa de un id nuevo.

## Orden

1. Backend merge → id publicado.
2. Cliente: registro + CONTEXTO + implementación UI.
3. Espejo UI en `50-sistema-integral/` citando id en páginas que llaman al API.

## Checklist PR frontend

- [ ] Registro: ref externa a ficha servidor
- [ ] CONTEXTO: ids usados listados
- [ ] Sin copy-paste de OpenAPI/ficha del backend
- [ ] `mapa-capas.md` alineado
- [ ] BFF propio → ficha local si aplica

## Repo aislado

Todo lo necesario está en **este** `docs/`; no abrir pack servidor salvo instrucción multi-repo explícita.

## Monorepo

Ver [monorepo-docs-fusionados.md](monorepo-docs-fusionados.md).

## Referencias

- [sync-documentacion-pr.md](sync-documentacion-pr.md)
- [PROTOCOLO.md](../PROTOCOLO.md)
