# Adopción del pack — primer mes

Roadmap humano tras [instalacion-docs.md](instalacion-docs.md). Para la **primera vez** (greenfield o migración), usar la instrucción completa [_PLANTILLA-adopcion-inicial-pack.md](../05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md).

## Semana 1 — Pegar pack

- [ ] Copiar pack a `docs/` + `AGENTES.md` en raíz
- [ ] Rellenar [configuracion-proyecto.md](../00-nucleo/configuracion-proyecto.md)
- [ ] Ejecutar smoke en [instalacion-docs.md](instalacion-docs.md)
- [ ] (Opcional) Lanzar instrucción adopción inicial y obtener aprobación

## Semana 2 — Primera área

- [ ] Crear `25-areas/<dominio>/CONTEXTO.md`
- [ ] Mapear endpoints existentes → `15-rutas/`
- [ ] Primera instrucción real de feature con [_PLANTILLA.md](../05-instrucciones/_PLANTILLA.md)

## Semana 3 — Espejo inicial

- [ ] Instrucción [_PLANTILLA-generar-espejo-integral.md](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md) modo `generar`
- [ ] Verificar `50-sistema-integral/` 1:1 con raíces configuradas
- [ ] Multi-repo: [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md) + [sync-multi-repo.md](sync-multi-repo.md)

## Semana 4 — Herramientas y cobertura

- [ ] Revisar propuestas en `35-herramientas/propuestas/` (si hay)
- [ ] Humano promueve una ficha útil → [\_PLANTILLA-promover-desde-propuesta.md](../35-herramientas/_PLANTILLA-promover-desde-propuesta.md)
- [ ] Validar excepción: agente ejecuta sin instrucción nueva dentro del alcance
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

- [flujo-instrucciones-documentacion.md](flujo-instrucciones-documentacion.md)
- [ciclo-integral-actos.md](ciclo-integral-actos.md)
- [monorepo-docs-fusionados.md](monorepo-docs-fusionados.md) (si aplica)
