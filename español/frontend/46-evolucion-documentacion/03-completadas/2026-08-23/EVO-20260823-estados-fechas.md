---
id: EVO-20260823-estados-fechas
status: done
source: human
tipo: taxonomia
impacto: ambos
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio: []
proposed_at: 2026-08-23
instruction_derivada: null
---

# EVO-20260823 — Organización por estados y fechas + alcance explícito de 46

## Cambio aplicado

Reorganización estructural del sistema documental para soportar crecimiento de miles de archivos sin perder navegabilidad:

1. **Estados + fechas (R-17):** todas las secciones acumulativas (`05-instrucciones`, `20-decisiones`, `40-auditorias`, `45-mejoras-propuestas`, `46-evolucion-documentacion`, `35-herramientas/propuestas`) se organizan en carpetas de estado `01-pendientes` … `06-listas-para-eliminar`, y dentro de cada estado en carpetas `YYYY-MM-DD` (fecha de creación). Cambio de estado = mover archivo (conservando la carpeta de fecha) + actualizar `status`.
2. **Alcance de 46 (R-18):** `46-evolucion-documentacion/` almacena únicamente mejoras del **sistema documental completo** (pack, taxonomía, convenciones, plantillas, metodología). Nunca documentación funcional de un proyecto. Bugs → 45 (`tipo: bug`); investigaciones → 40.
3. **Integraciones:** el panel `decisiones-pendientes` mueve fichas entre carpetas de estado al aplicar decisiones (nuevas acciones: `eliminar` → 06; promovida → `03-completadas`); el validador verifica la estructura de estados; `verificar-paridad.sh` soporta packs `backend/frontend` y patrones `*`; alias `AGENTS.md`; `ESTADO.md` de orientación; guía canónica `10-guias/organizacion-estados-fechas.md`.
4. **Simplificación:** los INDICE de secciones acumulativas dejan de mantener tablas manuales — el árbol de carpetas es el índice; vista viva vía `decisiones.py scan`.

## Aprobación

Decisión humana explícita en sesión, 2026-08-23 (refactorización ordenada por el humano). Registrada en [CHANGELOG.md](../../../CHANGELOG.md) `[1.0.0]`.

## Relación con matriz

Fila «Organización por estados y fechas» añadida a [matriz-cobertura-proyectos.md](../../matriz-cobertura-proyectos.md).
