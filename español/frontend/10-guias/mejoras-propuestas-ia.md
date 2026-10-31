# Mejoras y deuda técnica — propuestas IA (cliente)

Guía para **registrar sin ejecutar** mejoras detectadas durante el trabajo normal en UI/BFF.

## Problema que resuelve

Sin este apartado, la IA tiende a:

- Refactorizar “de paso” → desvía el alcance y consume tokens.
- Olvidar deuda detectada → se pierde el hallazgo.
- Confundir mejora con herramienta reutilizable → usar `35-herramientas/propuestas/` solo para scripts.

`45-mejoras-propuestas/` es la **cola humana**: captura, prioriza, aprueba después.

## Cuándo la IA debe registrar

| Situación | Acción |
|-----------|--------|
| Refactor UI útil pero **no pedido** en la instrucción | Ficha en `45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/` |
| Bug **dentro** del alcance actual | Arreglar en la misma instrucción |
| Bug **fuera** del alcance | Ficha en `45-mejoras-propuestas/01-pendientes/` con `tipo: bug` |
| Investigación profunda / varios hallazgos | Auditoría en `40-auditorias/02-en-progreso/` |
| Script reutilizable | `35-herramientas/propuestas/01-pendientes/` |
| Mejora **pedida** por el humano | Instrucción normal, no bandeja 45 |
| Gap del **sistema documental completo** (pack, taxonomía, plantillas) | `46-evolucion-documentacion/01-pendientes/` (R-18; no docs de un proyecto) |

## 45 vs 46 — no confundir

| | `45-mejoras-propuestas/` | `46-evolucion-documentacion/` |
|--|--------------------------|----------------------------------|
| **Qué** | Deuda del producto UI/BFF (código, diseño repo, bugs) | **Solo** sistema documental completo (pack, taxonomía, convenciones, plantillas, metodología) |
| **NO es** | — | Documentación funcional de un proyecto/módulo/feature (R-18) |
| **Cuándo** | Fuera de alcance en instrucción | Gap detectado en adopción o evolución general del sistema documental |
| **Máx. por cierre** | 3 | 2 |
| **Matriz** | — | [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md) |
| **Protocolo** | [_PROTOCOLO 45](../45-mejoras-propuestas/_PROTOCOLO.md) | [_PROTOCOLO 46](../46-evolucion-documentacion/_PROTOCOLO.md) |

## Cuándo la IA no debe registrar

- Nitpicks triviales sin impacto.
- Preferencias de estilo ya cubiertas por linter/formatter.
- Más de **3 propuestas** en un mismo cierre (priorizar las más relevantes).

## Flujo IA (al cerrar instrucción)

1. Completar alcance solicitado primero.
2. Si quedó mejora fuera de alcance → crear ficha desde [_PLANTILLA-propuesta.md](../45-mejoras-propuestas/_PLANTILLA-propuesta.md) en `01-pendientes/YYYY-MM-DD/`.
3. Añadir id a `mejoras_propuestas` en frontmatter de la instrucción.
4. **No** tocar código de la mejora.

## Flujo humano (revisión periódica de pendientes)

1. Revisar pendientes con `python3 docs/scripts/decisiones/decisiones.py scan` semanal o por sprint.
2. Enriquecer ficha con notas de negocio.
3. Aprobar → [_PLANTILLA-revisar-propuesta.md](../45-mejoras-propuestas/_PLANTILLA-revisar-propuesta.md) → nueva instrucción + `02-en-progreso/`.
4. Rechazar → `05-canceladas/`.

(En Windows: `py -3` en lugar de `python3`.)

Ficha: [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md).

## Regla anti-desvío

> **Resuelve lo crítico y lo solicitado.** Lo demás va a `45-mejoras-propuestas/` o `46-evolucion-documentacion/`, no al PR actual.

## Referencias

- [_PROTOCOLO.md](../45-mejoras-propuestas/_PROTOCOLO.md)
- [_PROTOCOLO 46](../46-evolucion-documentacion/_PROTOCOLO.md)
- [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md)
- [estrategia-instrucciones.md](../00-nucleo/estrategia-instrucciones.md)
- [herramientas-autorizadas-vs-propuestas.md](herramientas-autorizadas-vs-propuestas.md)
