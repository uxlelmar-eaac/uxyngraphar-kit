# Adopción del pack — primer mes (cliente)

Roadmap para repo frontend **aislado**. Primera adopción: [_PLANTILLA-adopcion-inicial-pack.md](../05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md).

## Semana 1 — Pegar pack

- [ ] `docs/` + `AGENTES.md` en raíz
- [ ] [configuracion-proyecto.md](../00-nucleo/configuracion-proyecto.md) + URL repo backend
- [ ] [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md) vacío listo
- [ ] Smoke: [instalacion-docs.md](instalacion-docs.md)

## Semana 2 — Primera área UI

- [ ] `25-areas/<feature>/CONTEXTO.md` con ids API
- [ ] BFF propios → `15-rutas/` si existen
- [ ] Primera instrucción feature

## Semana 3 — Espejo UI

- [ ] Generar espejo bajo raíces UI
- [ ] `mapa-capas.md`: feature ↔ id API (refs externas)

## Semana 4 — Herramienta autorizada

- [ ] Promover una ficha UI útil desde propuestas
- [ ] Revisar [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md); registrar gaps en `46-evolucion-documentacion/` si aplica

## Perfil mínimo (proyectos pequeños)

Para repos chicos o personales puede adoptarse solo el núcleo e ir graduando. Registrar el perfil en [configuracion-proyecto.md](../00-nucleo/configuracion-proyecto.md).

| Se adopta desde el día 1 | Se activa al crecer |
|--------------------------|---------------------|
| `AGENTES.md`, `REGLAS.md`, `PROTOCOLO.md` | Espejo `50-sistema-integral/` + registro de cobertura |
| `05-instrucciones/` (plantilla estándar + solo-docs) | Cola `46-evolucion-documentacion/` + matriz |
| `25-areas/` (1 CONTEXTO) y `15-rutas/` | `35-herramientas/` y auditorías formales |
| Cola `45-mejoras-propuestas/` | CI estricto (`STRICT_*`) |

Criterio de graduación: al superar ~3 áreas o ~15 instrucciones cerradas, activar la política de espejo incremental y la revisión trimestral de 46.

## Referencias

- [sync-multi-repo.md](sync-multi-repo.md)
- [ciclo-integral-actos.md](ciclo-integral-actos.md)
- [PROTOCOLO.md](../PROTOCOLO.md) — repo aislado
