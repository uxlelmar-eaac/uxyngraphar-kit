# Visión — documentación general del sistema

Este documento declara **qué persigue** el estándar de documentación de este repositorio y cómo debe usarse por humanos y agentes de código.

## Objetivo

Mantener **documentación general de todo el sistema** (capa cliente) que:

1. Describe arquitectura UI, restricciones, glosario y convenciones transversales (`00-nucleo/`).
2. Se complementa con guías (`10-guias/`) y manuales operativos (`30-manuales/`).
3. Permite capacitación **por dominio** sin volcar todo `docs/` (`25-areas/`).
4. Permanece **alineada con el código** mediante anclas, sync en cada PR y reglas duras del [PROTOCOLO.md](../PROTOCOLO.md).

## Principios

| Principio | Significado |
|-----------|-------------|
| Consecutividad | Siempre seguir la secuencia de lectura definida en PROTOCOLO y AGENTES; nunca “leer todo docs/” por defecto |
| Alineación | Cambio de código → actualización documental en el **mismo cambio/PR** |
| Eficiencia IA | Lectura acotada por instrucción; ver [eficiencia-ia.md](eficiencia-ia.md) |
| Trazabilidad | Toda orden de ejecución humana → instrucción en `05-instrucciones/<estado>/YYYY-MM-DD/`; toda investigación no trivial → audit en `40-auditorias/02-en-progreso/` |
| Instrucción como contrato | Toda lectura y escritura documental (operativa y espejo) definida en la instrucción aprobada; ver [estrategia-instrucciones.md](estrategia-instrucciones.md) |
| Promoción | Hallazgos permanentes se promueven a canon, ADR o ficha; no quedan solo en auditorías archivadas |
| Exclusividad de rutas | Manejadores BFF propios en `15-rutas/`; rutas del servidor citadas por `id`, **sin duplicar** |

## Secuencia de lectura (agente y personal)

1. [AGENTES.md](../../AGENTES.md) en la raíz del repo
2. Instrucción aprobada de la tarea (`05-instrucciones/`)
3. [CONTEXTO.md](../25-areas/) del área declarada
4. Fichas BFF citadas en `15-rutas/`; API servidor por `id` del catálogo backend
5. Código por anclas del CONTEXTO o de la ficha
6. Auditorías `02-en-progreso/` solo si investiga
7. Manuales solo en tareas operativas

Detalle completo: [PROTOCOLO.md](../PROTOCOLO.md) sección “Secuencia de lectura del agente”.

## Mapa de la documentación general

| Sección | Rol en la visión general |
|---------|--------------------------|
| [00-nucleo/](INDICE.md) | Canon del cliente: arquitectura UI, plantilla de funcionalidad, glosario, restricciones |
| [10-guias/](../10-guias/) | Incorporación, pruebas, contratos API |
| [30-manuales/](../30-manuales/) | Despliegue e incidentes |
| [20-decisiones/](../20-decisiones/) | ADRs — decisiones arquitectónicas persistentes |

Las secciones `05-instrucciones/`, `20-decisiones/`, `40-auditorias/`, `45-mejoras-propuestas/` y `46-evolucion-documentacion/` se organizan por **estados y fechas** ([organizacion-estados-fechas.md](../10-guias/organizacion-estados-fechas.md)); `15-rutas/` y `25-areas/` son registros **modulares** por dominio. Complementan el núcleo pero no lo sustituyen.

## Relación con el repositorio servidor

- Fichas HTTP del API backend viven en el **repo servidor** (`docs/15-rutas/`).
- En este repo solo se documentan manejadores de ruta / BFF (`app/api/**`).
- Referenciar endpoints del servidor por `id` estable (p. ej. `modulo.recurso.accion`).
- **Sistema integral:** [`50-sistema-integral/`](../50-sistema-integral/INDICE.md) — espejo 1:1 del scaffolding UI. Estrategia: [estrategia-instrucciones.md](estrategia-instrucciones.md).

## Mantenimiento

Al adoptar este pack en un proyecto real:

1. Rellenar `00-nucleo/configuracion-proyecto.md` y adaptar arquitectura UI.
2. Crear áreas desde `_PLANTILLA.md`; citar API servidor por `id`.
