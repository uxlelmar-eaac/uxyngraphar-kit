# Checklist — sync documentación en PR

Usar en **cada pull request** que toque código o documentación del cliente. Objetivo: mantener docs alineadas con el código en el mismo cambio.

## Siempre

- [ ] Instrucción con `lectura_minima` y `anclas_codigo` rellenos (≤8 docs / ≤5 archivos código)
- [ ] ¿Hay instrucción `approved` para esta tarea?
- [ ] ¿Los archivos ancla en fichas y CONTEXTO apuntan a rutas que existen?
- [ ] ¿No se duplicaron fichas HTTP del servidor?
- [ ] ¿No quedaron hallazgos permanentes solo en una auditoría sin promoción?
- [ ] Code review (R-23): ¿el nombre elimina la necesidad de un comentario? Sin nombres genéricos ni constantes mágicas; comentarios solo para el porqué ([guía](../00-nucleo/nombres-autoexplicativos.md))

## Funcionalidad UI nueva

- [ ] `docs/25-areas/<id>/CONTEXTO.md` creado o actualizado
- [ ] Fila en `docs/25-areas/INDICE.md`
- [ ] Endpoints del servidor citados por **`id`** (no ficha duplicada)

## Manejador BFF / route handler propio

- [ ] Ficha en `docs/15-rutas/<módulo>/<método>-<path-slug>.md`
- [ ] Frontmatter con `id` estable (prefijo distinto al servidor si comparten nombre semántico)
- [ ] Fila en `docs/15-rutas/INDICE.md`
- [ ] Tabla actualizada en `25-areas/<módulo>/CONTEXTO.md`

## Consumo de API del servidor

- [ ] IDs referenciados existen en `15-rutas/INDICE.md` del repo servidor
- [ ] Tipos/cliente HTTP actualizados si cambió el contrato

## Instrucción cerrada

- [ ] Estado `done` + movida a `05-instrucciones/03-completadas/YYYY-MM-DD/` (R-17) + sección **Resultado** rellenada (operativa + espejo)

## Espejo integral (`50-sistema-integral`)

- [ ] Instrucción lista `espejo_actualizar` coherente con UI/BFF tocados
- [ ] `README.md` de carpetas afectadas refleja hijos actuales
- [ ] `.md` de pages/componentes relevantes describe rol actual (sin código pegado)
- [ ] IDs API citados en espejo (sin duplicar fichas del servidor)
- [ ] Refactor de rutas: `.md` movidos o migración en alcance de instrucción
- [ ] Resultado menciona archivos de espejo modificados

## Herramientas (`35-herramientas`)

- [ ] Nueva ficha **autorizada:** creada solo por humano; `status: authorized`; fila en `autorizadas/INDICE.md`
- [ ] Propuesta IA: ficha en `propuestas/01-pendientes/YYYY-MM-DD/` + `herramientas_propuestas` en instrucción; **no ejecutada**
- [ ] Propuesta revisada: promovida a `autorizadas/` o movida a `propuestas/05-canceladas/`
- [ ] PR que solo usa herramienta autorizada: excepción documentada (ficha + alcance)
- [ ] Scripts npm / codegen documentados en ficha, no sueltos en docs

## Mejoras propuestas (`45-mejoras-propuestas/`)

- [ ] Deuda/refactor/bug fuera de alcance → ficha en `01-pendientes/YYYY-MM-DD/` + `mejoras_propuestas` en instrucción
- [ ] **No implementada** en el mismo PR
- [ ] Humano revisa pendientes: aprobar → instrucción derivada + `02-en-progreso/`; rechazar → `05-canceladas/`
- [ ] (Opcional) Revisión de pendientes con [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md): `python3 docs/scripts/decisiones/decisiones.py scan`
- [ ] Máx. 3 propuestas por cierre

(En Windows: `py -3` en lugar de `python3`.)

## Auditoría cerrada

- [ ] Promociones aplicadas (canon, ADR, ficha o restricción)
- [ ] Archivo movido a `40-auditorias/03-completadas/YYYY-MM-DD/` (`status: cerrada`)
- [ ] Histórica → `04-archivadas/`; cancelada → `05-canceladas/`

## Promoción desde auditoría

Cuando un hallazgo en `40-auditorias/02-en-progreso/` cambia reglas permanentes:

| Paso | Acción |
|------|--------|
| 1 | Definir promociones en frontmatter (`tipo`: `canon` \| `adr` \| `ficha` \| `espejo`) |
| 2 | Crear o actualizar destino (CONTEXTO, ADR, ficha BFF `15-rutas/`, paths espejo) |
| 3 | Enlazar desde destino hacia la auditoría cerrada (opcional, una línea) |
| 4 | Sync `espejo_actualizar` si aplica |
| 5 | Mover auditoría a `03-completadas/`; quitar de `02-en-progreso/` |
| 6 | Actualizar destinos citados (CONTEXTO, registro de ids, índices de registros) |
| 7 | Instrucción de cierre o PR dedicado con Resultado listando promociones |

**No dejar** la verdad solo en la auditoría activa.
