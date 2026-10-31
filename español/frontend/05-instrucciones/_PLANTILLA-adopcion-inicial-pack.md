---
id: YYYYMMDD-001-adopcion-inicial-pack
status: plantilla
source: human
created: YYYY-MM-DDTHH:MM:SSZ
approved_at: null
executed_at: null
scope: [adopcion, uxyngraphar]
areas: []
acto: adoptar
vinculos_entrada: []
vinculos_salida: []
lectura_minima:
  - docs/00-nucleo/configuracion-proyecto.md
  - docs/10-guias/instalacion-docs.md
  - docs/PROTOCOLO.md
  - AGENTES.md
anclas_codigo: []
espejo_actualizar: []
espejo_leer: []
herramientas_propuestas: []
mejoras_propuestas: []
evolucion_documentacion: []
presupuesto_max_docs: 12
presupuesto_max_archivos_codigo: 15
tipo: adopcion-inicial-pack
fases:
  - escaneo
  - configuracion
  - migracion_o_greenfield
  - areas_iniciales
  - espejo_inicial
  - smoke
---

# YYYYMMDD-001 — Adopción inicial del pack documental (cliente)

> **Contrato IA:** frontmatter + secciones hasta **Decisión a tomar**. Fases detalladas en **Anexo**.

> **Plantilla compleja — primera vez.** Repo frontend **aislado** del backend. Copiar, renombrar fecha, aprobar y ejecutar por fases.

## Pedido (síntesis)

- Pegar y configurar el pack `docs/` en el repositorio frontend.
- Rellenar identidad del proyecto, registro ids API (ref al repo servidor).
- Migrar docs UI existentes **o** arrancar greenfield.
- Crear 1–2 áreas UI iniciales, espejo base y verificar smoke.

## Objetivo

Al cerrar: `AGENTES.md` en raíz del repo, `configuracion-proyecto.md` completo, al menos un `CONTEXTO.md`, espejo inicial bajo raíces UI configuradas, ids API en registro (no fichas duplicadas), índices actualizados y smoke OK.

## Vínculos del acto

- **Entrada:** primera adopción del pack frontend (greenfield o migración) — `vinculos_entrada: []` o issue de adopción
- **Contexto mínimo:** coincide con `lectura_minima` + guías de instalación/adopción
- **Salida esperada:** áreas UI, espejo, matriz 46 actualizada; fichas `EVO-*` si gaps (≤2) — rellenar `vinculos_salida` al cerrar

Ver [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md).

---

## Anexo — Fases de adopción

> **IA:** consultar solo las fases declaradas en el plan aprobado.

## Fase 1 — Escaneo del repositorio

**Anclas sugeridas** (ajustar al proyecto):

- `<src/app/>`, `<src/components/>`, `<src/features/>`
- BFF/routes si existen
- Documentación existente: `<README.md>`, `<docs/>`, `<wiki/>`

**Entregables:**

- [ ] Mapa de features/páginas detectados
- [ ] Cliente HTTP hacia API identificado
- [ ] Inventario de docs existentes (si hay)
- [ ] URL/repo del backend para registro ids
- [ ] ¿Monorepo o repo aislado? → anotar en plan

---

## Fase 2 — Configuración del pack

- [ ] Copiar contenido del pack cliente a `docs/` del repo (o ruta acordada)
- [ ] Copiar `AGENTES.md` a **raíz del repositorio**
- [ ] Rellenar [configuracion-proyecto.md](../00-nucleo/configuracion-proyecto.md): identidad, rutas código, espejo, repos relacionados
- [ ] Rellenar [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md) — refs al repo servidor (URL/path), **no paths locales cruzados**
- [ ] Verificar colas 35/45/46 vacías (solo plantillas e índices)
- [ ] Ejecutar smoke: [instalacion-docs.md](../10-guias/instalacion-docs.md) sección final

---

## Fase 3 — Migración o greenfield

### Si el repo **ya tiene documentación**

- [ ] Clasificar docs existentes: operativa | espejo | obsoleto
- [ ] Mapear a taxonomía `00`–`90` (CONTEXTO UI → `25-areas/`, BFF → `15-rutas/`, etc.)
- [ ] Mover obsoletos a `90-archivo/` con nota de origen
- [ ] **No** duplicar: una sola fuente de verdad por tema
- [ ] Endpoints API: solo **id** + ref registro; no copiar fichas del servidor
- [ ] Registrar gaps en plan (qué falta crear) → fichas `46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` + [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md)

### Si es **greenfield** (sin docs)

- [ ] Identificar 1–2 áreas UI principales (p. ej. `dashboard`, `auth-ui`)
- [ ] Saltar migración; ir directo a Fase 4

---

## Fase 4 — Áreas iniciales

Por cada área (mínimo 1, recomendado 2):

- [ ] Crear `25-areas/<id>/CONTEXTO.md` desde [_PLANTILLA.md](../25-areas/_PLANTILLA.md) con refs a ids API
- [ ] Mapa de lectura: anclas código, fichas `15-rutas/` existentes o planificadas
- [ ] BFF propios → `15-rutas/` si existen
- [ ] Actualizar [25-areas/INDICE.md](../25-areas/INDICE.md)

---

## Fase 5 — Espejo inicial

- [ ] Crear instrucción hija o usar modo `generar` de [_PLANTILLA-generar-espejo-integral.md](_PLANTILLA-generar-espejo-integral.md)
- [ ] Raíces UI desde `configuracion-proyecto.md`
- [ ] Espejo 1:1 bajo `50-sistema-integral/` (solo `.md`)
- [ ] Actualizar `50-sistema-integral/mapa-capas.md`: feature ↔ id API

**Presupuesto:** esta fase puede ampliar `presupuesto_max_archivos_codigo` para inspección de estructura (solo lectura).

---

## Fase 6 — Smoke y cierre

- [ ] `AGENTES.md` en raíz apunta a `docs/`
- [ ] [INDICE.md](../INDICE.md) raíz del pack revisado
- [ ] Script opcional: `python3 docs/scripts/validar-documentacion.py`
- [ ] Primera instrucción real de feature (no plantilla) lista para usar `_PLANTILLA.md`
- [ ] Marcar esta instrucción `done` con Resultado completo

---

## Plan de ejecución (aprobar antes de actuar)

1. Fase 1 escaneo → actualizar sección Anclas en esta instrucción.
2. Fase 2 configuración.
3. Fase 3 según rama (migración | greenfield).
4. Fase 4 áreas.
5. Fase 5 espejo.
6. Fase 6 smoke.

## Criterios de aceptación

- [ ] Repo aislado operativo sin depender del pack servidor en disco
- [ ] No quedan placeholders críticos en `configuracion-proyecto.md`
- [ ] Registro ids con refs externas al backend
- [ ] ≥1 CONTEXTO en `25-areas/`
- [ ] Espejo inicial con README en raíces configuradas
- [ ] Smoke checklist verde
- [ ] Sin secretos en docs migrados

## Riesgos / no tocar

- No reescribir código de negocio en esta instrucción (salvo anclas mínimas para inventario).



## Decisión a tomar

> Solo cuando `status: awaiting_approval`.

<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** — cambiar a `status: approved` y fijar `approved_at`
- [ ] <!-- decision:cancelar --> **Cancelar** — cambiar a `status: cancelled`

## Resultado (status: done)

- Repo configurado:
- Áreas creadas:
- Espejo paths:
- Docs migrados (si aplica):
- Registro ids:
- Pendientes humanos:

---

## Costo en tokens

> Automático: `decisiones.py new` abre «Creación de la instrucción», `contexto.py` abre «Implementación» y `decisiones.py cerrar` escribe aquí la tabla por fases (análisis, instrucción, implementación, verificación, cierre) con el total. El agente marca `verificacion` y `cierre` al empezarlas: `python3 docs/scripts/costo-tokens.py fase <id> <fase>`. Guía: [costo-tokens.md](../10-guias/costo-tokens.md).

<!-- tokens:inicio -->
Pendiente: se mide al cerrar la instrucción.
<!-- tokens:fin -->

---

## Anexo — Checklist humano / PR

> **IA:** no leer esta sección durante planificación ni implementación; solo al cerrar la instrucción.

### Matriz 46 al cerrar

- [ ] [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md)
- [ ] Revisión de pendientes: [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md)

### Registro de cobertura (si política incremental activa)

- [ ] Actualizar [registro-cobertura-espejo.md](../50-sistema-integral/registro-cobertura-espejo.md) al cerrar si hubo paths en `espejo_actualizar`

### Mejora / deuda fuera de alcance (opcional)

- [ ] Ficha en `docs/45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/` + `mejoras_propuestas` (máx. 3; bugs con `tipo: bug`)

### Evolución documental (opcional)

- [ ] Ficha en `docs/46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` + `evolucion_documentacion` (máx. 2; solo sistema documental completo — R-18)
