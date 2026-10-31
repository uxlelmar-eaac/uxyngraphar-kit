---
id: YYYYMMDD-NNN
status: awaiting_approval
source: human
created: YYYY-MM-DDTHH:MM:SSZ
approved_at: null
executed_at: null
scope: [documentacion]
areas: []
acto: mejorar-docs
vinculos_entrada: []
vinculos_salida: []
lectura_minima: []
anclas_codigo: []
espejo_actualizar: []
espejo_leer: []
herramientas_propuestas: []
mejoras_propuestas: []
evolucion_documentacion: []
presupuesto_max_docs: 8
presupuesto_max_archivos_codigo: 0
related_audits: []
related_endpoints: []
tipo: solo-documentacion
---

# YYYYMMDD-NNN — Título (solo documentación)

> **Contrato IA:** frontmatter + secciones hasta **Decisión a tomar**. El **Anexo** es checklist humano/PR — la IA solo lo consulta al **cerrar** (`status: done`).

## Pedido (síntesis)

- Actualizar docs operativas y/o espejo de módulos sin tocar código.

## Objetivo

Una frase.

## Vínculos del acto

- **Entrada:** …
- **Contexto mínimo:** coincide con `lectura_minima`
- **Salida esperada:** operativa ± espejo; cola 46 si gap pack

Ver [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md).

## Lectura mínima (IA)

- [ ] `docs/25-areas/<area>/CONTEXTO.md`

Guía humana: [redaccion-lectura-minima.md](../10-guias/redaccion-lectura-minima.md).

## Anclas de código

**Ninguna** — `anclas_codigo: []`.

## Plan de ejecución (aprobar antes de escribir)

1. Leer `lectura_minima`.
2. Editar docs operativas.
3. Sync espejo (`espejo_actualizar`).
4. Cerrar con Resultado.

## Criterios de aceptación

- [ ] Cero archivos de código modificados
- [ ] Docs operativas y espejo alineados

## Decisión a tomar

> Solo cuando `status: awaiting_approval`.

<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** — cambiar a `status: approved` y fijar `approved_at`
- [ ] <!-- decision:cancelar --> **Cancelar** — cambiar a `status: cancelled`

## Resultado (al cerrar, status: done)

- Docs operativas:
- Espejo (`espejo_actualizar`):
- Evolución documental (`evolucion_documentacion`):
- Vínculos de salida (`vinculos_salida`):

---

## Costo en tokens

> Automático: `decisiones.py new` abre «Creación de la instrucción», `contexto.py` abre «Implementación» y `decisiones.py cerrar` escribe aquí la tabla por fases (análisis, instrucción, implementación, verificación, cierre) con el total. El agente marca `verificacion` y `cierre` al empezarlas: `python3 docs/scripts/costo-tokens.py fase <id> <fase>`. Guía: [costo-tokens.md](../10-guias/costo-tokens.md).

<!-- tokens:inicio -->
Pendiente: se mide al cerrar la instrucción.
<!-- tokens:fin -->

---

## Anexo — Checklist humano / PR

> **IA:** no leer esta sección durante planificación ni implementación; solo al cerrar.

### Sync documental

| Capa | Qué | Paths |
|------|-----|-------|
| Operativa | CONTEXTO / fichas HTTP / índice | … |
| Espejo | `50-sistema-integral/` | `espejo_actualizar` |

### Evolución documental / cobertura pack (opcional)

- [ ] Ficha en `docs/46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` + `evolucion_documentacion` (máx. 2; solo sistema documental completo — R-18)
- [ ] Actualizar [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md)

Ver [_PROTOCOLO 46](../46-evolucion-documentacion/_PROTOCOLO.md).
