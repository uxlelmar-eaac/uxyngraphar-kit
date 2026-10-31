---
id: YYYYMMDD-NNN
status: awaiting_approval
source: human
created: YYYY-MM-DDTHH:MM:SSZ
approved_at: null
executed_at: null
scope: [uxyngraphar]
areas: []
acto: mejorar-docs
vinculos_entrada: []
vinculos_salida: []
lectura_minima:
  - docs/50-sistema-integral/registro-cobertura-espejo.md
  - docs/50-sistema-integral/_PROTOCOLO.md
  - docs/50-sistema-integral/_PLANTILLA-README-carpeta.md
  - docs/00-nucleo/configuracion-proyecto.md
anclas_codigo: []           # rellenar: solo raíces o paths con huecos (lista cerrada)
espejo_actualizar: []       # rellenar al cerrar: solo paths nuevos o actualizados
espejo_leer: []             # opcional: ≤3 README existentes para coherencia de tono
herramientas_propuestas: []
mejoras_propuestas: []
evolucion_documentacion: []
presupuesto_max_docs: 10
presupuesto_max_archivos_codigo: 0
related_audits: []
related_endpoints: []
tipo: consolidar-espejo-integral
modo: rellenar-huecos
paths_huecos: []            # lista cerrada humana; no escanear repo entero
---

# YYYYMMDD-NNN — Consolidar documentación integral (solo huecos)

> **Contrato IA:** frontmatter + secciones hasta **Decisión a tomar**. El **Anexo** es checklist humano/PR — la IA solo lo consulta al **cerrar** (`status: done`).

## Pedido

- Pedido humano tipo «documentación general del sistema» / «completar el espejo».
- **Asunción:** meses de instrucciones incrementales ya crearon gran parte del espejo.
- Esta tarea **no** recorre todo el repo: solo **huecos** listados en el registro o en `paths_huecos`.

## Objetivo

Mapa integral **utilizable** con coste de tokens **bajo**: leer registro → procesar lista cerrada de faltantes → actualizar índice/visión si aplica.

## Vínculos del acto

- **Entrada:** política incremental activa + registro con historial — `vinculos_entrada`
- **Contexto mínimo:** registro + protocolo espejo + raíces config
- **Salida esperada:** huecos cerrados listados en `espejo_actualizar` y registro actualizado

Ver [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md) · Guía: [espejo-incremental-proyectos-grandes.md](../10-guias/espejo-incremental-proyectos-grandes.md).

## Lectura mínima (IA)

- [ ] [`registro-cobertura-espejo.md`](../50-sistema-integral/registro-cobertura-espejo.md) — **primero** (estado y huecos)
- [ ] [`_PROTOCOLO.md`](../50-sistema-integral/_PROTOCOLO.md)
- [ ] Plantillas `_PLANTILLA-README-carpeta` / `_PLANTILLA-archivo`
- [ ] Sección Espejo en `configuracion-proyecto.md`

**Prohibido:** listar o leer todo `50-sistema-integral/`; glob masivo en código.

## Derivar paths_huecos (lista cerrada)

Completar **solo** una de estas fuentes (prioridad):

1. Sección **Huecos conocidos** del registro (humano ya priorizó).
2. Frontmatter `paths_huecos` (aprobado en plan).
3. Comparación acotada: una raíz a la vez, máx. **N paths** según presupuesto (declarar N en alcance).

Ejemplo frontmatter:

```yaml
paths_huecos:
  - src/common/guards/
  - src/modules/reporting/report.service.ts
```

## Plan de ejecución (aprobar antes de escribir)

1. Leer registro: qué ya está cubierto (no reescribir).
2. Por cada path en `paths_huecos`:
   - Carpeta → `README.md` en espejo.
   - Archivo relevante → `<nombre>.md`.
3. Actualizar `registro-cobertura-espejo.md` (cobertura + historial con esta instrucción).
4. Si aplica: una línea en `50-sistema-integral/INDICE.md` o `vision-espejo.md` (sin volcar árbol).
5. **No** borrar `.md` existentes; **no** pegar código.

## Diferencia vs generar masivo

| | Consolidar (esta plantilla) | Generar masivo |
|--|----------------------------|----------------|
| Lectura | Registro + lista cerrada | Raíces enteras |
| Escritura | Solo huecos | Todo el scaffolding |
| Cuándo | Proyecto grande con incremental previo | Proyecto pequeño o repo vacío de espejo |
| Tokens | Bajo | Alto |

## Alcance

- **Incluye:** paths en `paths_huecos`; registro; opcional INDICE raíz del espejo.
- **Excluye:** re-sync total; `25-areas/`; código fuente.
- **Presupuesto paths nuevos:** _(ej. máx. 12 archivos .md por sesión — ampliar con aprobación)_

## Criterios de aceptación

- [ ] Solo paths declarados tocados (verificable vs registro previo)
- [ ] Registro actualizado con esta instrucción en historial
- [ ] Ningún código en el espejo
- [ ] Huecos restantes listados explícitamente en Resultado (para otra consolidación)



## Decisión a tomar

> Solo cuando `status: awaiting_approval`.

<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** — cambiar a `status: approved` y fijar `approved_at`
- [ ] <!-- decision:cancelar --> **Cancelar** — cambiar a `status: cancelled`

## Resultado (al cerrar, status: done)

- Paths creados/actualizados (`espejo_actualizar`):
- Huecos que quedan para otra sesión:
- Registro actualizado: sí / no
- `vinculos_salida`:

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
