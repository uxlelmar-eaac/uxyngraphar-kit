---
id: EVO-20260823-cli-andamiaje
status: done
source: human
tipo: herramienta-pack
impacto: ambos
prioridad: despues
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/decisiones/plantillas.py
  - 35-herramientas/autorizadas/
proposed_at: 2026-08-23
instruction_derivada: solicitud-humana-20261015
---
# EVO-20260823 — CLI de andamiaje de instrucciones y fichas

## Qué falta hoy

Crear instrucciones es manual (copiar plantilla, renombrar, rellenar frontmatter, respetar NNN del día). Errores de formato y fricción frecuentes.

## Propuesta de cambio

Comando `python3 docs/scripts/decisiones/plantillas.py new instruccion --acto crear --areas billing --slug ...` que:

- Copia la plantilla a `05-instrucciones/01-pendientes/YYYY-MM-DD/<slug>.md` con frontmatter pre-rellenado (id auto-incrementado).
- Pre-valida enums (`acto`, `status`, `tipo`) contra [convenciones-frontmatter.md](../../../00-nucleo/convenciones-frontmatter.md).
- Subcomandos: `mejora`, `evo`, `auditoria`, `propuesta`, `adr` (misma mecánica por sección).
- Ficha de herramienta autorizada en `35-herramientas/autorizadas/`.

(En Windows: `py -3` en lugar de `python3`.)

## Decisión a tomar

<!-- decision-group: EVO-20260823-cli-andamiaje -->
- [x] <!-- decision:aprobar --> **Aprobar** → instrucción derivada
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar** → `05-canceladas/`

### Notas del humano

- [2026-10-15T22:27:26Z] decisiones-pendientes sesión 20261015-222712: aprobar

<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO EVO-20260823-cli-andamiaje -->
