---
id: YYYYMMDD-NNN
status: awaiting_approval
source: human
created: YYYY-MM-DDTHH:MM:SSZ
approved_at: null
executed_at: null
scope: [uxyngraphar, politica-proyecto]
areas: []
acto: adoptar
vinculos_entrada: []
vinculos_salida: []
lectura_minima:
  - docs/00-nucleo/estrategia-instrucciones.md
  - docs/10-guias/espejo-incremental-proyectos-grandes.md
  - docs/50-sistema-integral/registro-cobertura-espejo.md
anclas_codigo: []           # opcional: raíces a inspeccionar solo para estimar tamaño
espejo_actualizar: []       # normalmente vacío; esta instrucción no genera espejo masivo
espejo_leer: []
herramientas_propuestas: []
mejoras_propuestas: []
evolucion_documentacion: []
presupuesto_max_docs: 6
presupuesto_max_archivos_codigo: 0
related_audits: []
related_endpoints: []
tipo: politica-espejo-incremental
---

# YYYYMMDD-NNN — Adoptar espejo incremental (proyecto mediano/grande)

> **Contrato IA:** frontmatter + secciones hasta **Decisión a tomar**. El **Anexo** es checklist humano/PR — la IA solo lo consulta al **cerrar** (`status: done`).

## Pedido

- El proyecto es **mediano, grande o muy grande**; un volcado único del espejo sería costoso en tokens y tiempo.
- A partir de ahora, **cada instrucción de feature** construye también su trozo de `50-sistema-integral/`.
- Cuando más adelante se pida «documentación general del sistema», ya habrá cobertura parcial y el coste será bajo.

## Objetivo

Política **activa** en el repo: sync incremental obligatorio + registro de cobertura actualizado en cada cierre. **No** ejecutar generación masiva del espejo salvo consolidación explícita posterior.

## Vínculos del acto

- **Entrada:** adopción del pack o cambio de escala del proyecto — `vinculos_entrada`
- **Contexto mínimo:** estrategia + guía incremental + registro vacío o parcial
- **Salida esperada:** `registro-cobertura-espejo.md` con `Política incremental: activa` + reglas en AGENTES/contexto humano

Ver [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md).

## Qué queda obligatorio tras aprobar

| Regla | Detalle |
|-------|---------|
| Toda instrucción con código | Rellenar `espejo_actualizar` desde `anclas_codigo` ([_PLANTILLA.md](_PLANTILLA.md)) |
| Al cerrar (`done`) | Actualizar [`registro-cobertura-espejo.md`](../50-sistema-integral/registro-cobertura-espejo.md) |
| Espejo masivo inicial | **No** usar [_PLANTILLA-generar-espejo-integral.md](_PLANTILLA-generar-espejo-integral.md) salvo proyecto pequeño o consolidación |
| Doc general futura | Usar [_PLANTILLA-consolidar-espejo-integral.md](_PLANTILLA-consolidar-espejo-integral.md) (solo huecos) |

## Lectura mínima (IA)

- [ ] [estrategia-instrucciones.md](../00-nucleo/estrategia-instrucciones.md) — reglas espejo
- [ ] [espejo-incremental-proyectos-grandes.md](../10-guias/espejo-incremental-proyectos-grandes.md)
- [ ] [registro-cobertura-espejo.md](../50-sistema-integral/registro-cobertura-espejo.md)

## Alcance

- **Incluye:** marcar política activa; documentar reglas para el equipo; opcionalmente listar raíces del repo y huecos iniciales en el registro.
- **Excluye:** generar espejo masivo; editar código de producto.
- **No tocar:** instrucciones históricas; espejo existente salvo corrección de metadatos del registro.

## Plan de ejecución (aprobar antes de escribir)

1. Confirmar tamaño del proyecto (raíces en `configuracion-proyecto.md`).
2. Actualizar `registro-cobertura-espejo.md`: `Política incremental: activa`, fecha, estado inicial de cobertura (inspección ligera de raíces si hace falta).
3. Añadir recordatorio en `AGENTES.md` o nota al humano: «usar _PLANTILLA estándar + espejo_actualizar en cada feature».
4. **No** lanzar `_PLANTILLA-generar-espejo-integral` en esta tarea.

## Criterios de aceptación

- [ ] Registro con política `activa` y criterio de actualización documentado
- [ ] Equipo/humano sabe: feature → espejo incremental; doc general → plantilla consolidar
- [ ] Cero generación masiva del espejo en esta instrucción



## Decisión a tomar

> Solo cuando `status: awaiting_approval`.

<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** — cambiar a `status: approved` y fijar `approved_at`
- [ ] <!-- decision:cancelar --> **Cancelar** — cambiar a `status: cancelled`

## Resultado (al cerrar, status: done)

- Registro actualizado:
- Notas al humano:
- `vinculos_salida`:
  - docs/50-sistema-integral/registro-cobertura-espejo.md

---

**Siguiente paso habitual:** instrucciones normales de producto con [_PLANTILLA.md](_PLANTILLA.md). Cuando el mapa esté maduro → [_PLANTILLA-consolidar-espejo-integral.md](_PLANTILLA-consolidar-espejo-integral.md).

---

## Costo en tokens

> Automático: `decisiones.py new` abre «Creación de la instrucción», `contexto.py` abre «Implementación» y `decisiones.py cerrar` escribe aquí la tabla por fases (análisis, instrucción, implementación, verificación, cierre) con el total. El agente marca `verificacion` y `cierre` al empezarlas: `python3 docs/scripts/costo-tokens.py fase <id> <fase>`. Guía: [costo-tokens.md](../10-guias/costo-tokens.md).

<!-- tokens:inicio -->
Pendiente: se mide al cerrar la instrucción.
<!-- tokens:fin -->

---

## Anexo — Checklist humano / PR

> **IA:** no leer esta sección durante planificación ni implementación; solo al cerrar la instrucción.

### Registro de cobertura (si política incremental activa)

- [ ] Actualizar [registro-cobertura-espejo.md](../50-sistema-integral/registro-cobertura-espejo.md) al cerrar si hubo paths en `espejo_actualizar`

### Mejora / deuda fuera de alcance (opcional)

- [ ] Ficha en `docs/45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/` + `mejoras_propuestas` (máx. 3; bugs con `tipo: bug`)

### Evolución documental (opcional)

- [ ] Ficha en `docs/46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` + `evolucion_documentacion` (máx. 2; solo sistema documental completo — R-18)
