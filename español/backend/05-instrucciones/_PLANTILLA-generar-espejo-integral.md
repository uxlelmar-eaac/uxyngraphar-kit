---
id: YYYYMMDD-NNN
status: awaiting_approval
source: human
created: YYYY-MM-DDTHH:MM:SSZ
approved_at: null
executed_at: null
scope: [uxyngraphar]
areas: []
acto: crear
vinculos_entrada: []
vinculos_salida: []
lectura_minima:
  - docs/00-nucleo/configuracion-proyecto.md
  - docs/50-sistema-integral/_PROTOCOLO.md
  - docs/50-sistema-integral/_PLANTILLA-README-carpeta.md
  - docs/50-sistema-integral/_PLANTILLA-archivo.md
anclas_codigo: []           # rellenar: raíces del scaffolding a inspeccionar
espejo_actualizar: []       # rellenar al cerrar: paths creados bajo 50-sistema-integral/
espejo_leer: []
herramientas_propuestas: []
mejoras_propuestas: []
evolucion_documentacion: []
presupuesto_max_docs: 8
presupuesto_max_archivos_codigo: 0   # esta tarea NO edita código fuente
related_audits: []
related_endpoints: []
tipo: generar-espejo-integral
---

# YYYYMMDD-NNN — Generar / actualizar espejo integral

> **Contrato IA:** frontmatter + secciones hasta **Decisión a tomar**. El **Anexo** es checklist humano/PR — la IA solo lo consulta al **cerrar** (`status: done`).

## Pedido

- Escanear el scaffolding del repo según raíces en `configuracion-proyecto.md`.
- Replicar **cada carpeta** bajo `docs/50-sistema-integral/` con la **misma ruta relativa** que en el proyecto.
- Crear **solo archivos `.md`**: `README.md` por carpeta; `<nombre-base>.md` por archivos de código relevantes.
- **No copiar código** ni crear archivos que no sean Markdown.

## Objetivo

Al terminar, cualquier persona puede recorrer `docs/50-sistema-integral/` como un mapa explicativo idéntico al árbol del repo.

## Vínculos del acto

- **Entrada:** necesidad de mapa espejo (adopción o resync) — `vinculos_entrada`
- **Contexto mínimo:** config espejo + plantillas 50
- **Salida esperada:** árbol `50-sistema-integral/` — listar paths en `vinculos_salida` y `espejo_actualizar` al cerrar

Ver [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md).

## Lectura mínima (IA)

- [ ] `docs/00-nucleo/configuracion-proyecto.md` (sección Espejo integral)
- [ ] `docs/50-sistema-integral/_PROTOCOLO.md`
- [ ] Plantillas `_PLANTILLA-README-carpeta.md` y `_PLANTILLA-archivo.md`

## Anclas de código (solo lectura para inspeccionar estructura)

Listar raíces a recorrer; no abrir archivos enteros salvo los necesarios para redactar `.md`:

- `<p. ej. src/>` — módulos de negocio
- `<p. ej. src/common/>` — transversal
- (añadir según proyecto)

## Alcance

- **Incluye:** carpetas bajo raíces declaradas; `README.md` en cada carpeta del espejo; `.md` de archivos clave (controllers, services, pages, handlers).
- **Excluye:** `node_modules/`, builds, `docs/`, tests unitarios archivo a archivo (solo README en carpeta `test/` si aplica).
- **Modo:** `generar` (vacío) | `resync` (solo nuevos) | `actualizar` (paths listados) | **`actualizar-parcial`** (lista cerrada abajo; no resync masivo)

## Modo actualizar-parcial

Usar cuando solo un subárbol cambió. **No** recorrer todo el repo.

1. Listar paths cerrados en frontmatter o sección **Paths parciales**:

```yaml
modo: actualizar-parcial
paths_parciales:
  - src/modules/auth/
  - src/common/guards/jwt.guard.ts
```

2. Por cada path:
   - Carpeta → `README.md` en espejo.
   - Archivo → `<nombre-base>.md` en espejo.
3. **No** tocar otras ramas del espejo.
4. Actualizar `mapa-capas.md` solo si afecta correspondencia multi-repo.

Distinto de `resync`: `actualizar-parcial` es lista explícita humana; `resync` detecta nuevos bajo raíces configuradas.

## Plan de ejecución (aprobar antes de escribir docs)

1. Leer raíces y exclusiones en `configuracion-proyecto.md`.
2. Listar árbol de directorios del repo (comando o exploración acotada a raíces).
3. Por cada carpeta del árbol (excepto exclusiones):
   - Crear `docs/50-sistema-integral/<ruta-espejo>/` si no existe.
   - Escribir o actualizar `README.md` desde plantilla (propósito, tabla de hijos, enlaces al código real).
4. Por cada archivo de código **relevante** (criterio: expone API, lógica de negocio, entrypoint, page/route):
   - Crear `<nombre-base>.md` en la misma carpeta del espejo.
   - Describir rol e interacciones **sin pegar código**.
5. Actualizar `50-sistema-integral/mapa-capas.md` si hay correspondencia con otro repo.
6. No tocar código fuente ni `25-areas/` salvo enlace desde README del espejo.

## Criterios de aceptación

- [ ] Toda carpeta bajo raíces configuradas tiene espejo con `README.md`.
- [ ] Ningún archivo en el espejo es código ejecutable.
- [ ] Rutas del espejo coinciden 1:1 con rutas del proyecto (relativas a raíz del repo).
- [ ] Meta (`_PROTOCOLO`, plantillas) intacta en raíz de `50-sistema-integral/`.

## Riesgos / no tocar

- No borrar `.md` existentes en resync sin listarlos en alcance.
- No volcar contenido de `15-rutas/`; solo enlazar.



## Decisión a tomar

> Solo cuando `status: awaiting_approval`.

<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** — cambiar a `status: approved` y fijar `approved_at`
- [ ] <!-- decision:cancelar --> **Cancelar** — cambiar a `status: cancelled`

## Resultado (al cerrar, status: done)

- Carpetas creadas:
- Archivos `.md` creados/actualizados:
- Pendientes humanos:

---

**Mantenimiento diario:** tras el espejo inicial, cada cambio de código usa sync incremental en [`_PLANTILLA.md`](_PLANTILLA.md) (`espejo_actualizar`), no esta plantilla masiva.

**Proyectos medianos/grandes:** no usar esta plantilla como primer paso. Adoptar [_PLANTILLA-politica-espejo-incremental.md](_PLANTILLA-politica-espejo-incremental.md) y consolidar después con [_PLANTILLA-consolidar-espejo-integral.md](_PLANTILLA-consolidar-espejo-integral.md). Ver [espejo-incremental-proyectos-grandes.md](../10-guias/espejo-incremental-proyectos-grandes.md).

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
