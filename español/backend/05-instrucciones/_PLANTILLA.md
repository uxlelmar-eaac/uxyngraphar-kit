---
id: YYYYMMDD-NNN
status: awaiting_approval
source: human
created: YYYY-MM-DDTHH:MM:SSZ
approved_at: null
executed_at: null
scope: []
areas: []
acto: crear
vinculos_entrada: []
vinculos_salida: []
lectura_minima: []          # lista cerrada de paths docs; la IA no abre otros
anclas_codigo: []           # rutas de código; preferir path:inicio-fin
espejo_actualizar: []       # paths docs/50-sistema-integral/... a crear o actualizar al cerrar
excepciones_reglas: []      # opcional: ["RP-NNN: motivo"]; vale solo si una persona aprueba la instrucción (96-reglas-proyecto)
espejo_leer: []             # default vacío; solo si hace falta consultar el espejo antes de actuar
herramientas_propuestas: [] # ids docs/35-herramientas/propuestas/... creados al cerrar (opcional)
mejoras_propuestas: []       # ids docs/45-mejoras-propuestas/... — deuda fuera de alcance (opcional, máx. 3)
evolucion_documentacion: []  # ids docs/46-evolucion-documentacion/... — sistema documental completo (opcional, máx. 2; R-18)
presupuesto_max_docs: 8
presupuesto_max_archivos_codigo: 5   # estándar; >5 solo con ampliación R-21 (floor(5 × ampliacion_factor))
ampliacion_factor: null            # R-21: 1.5–2 solo si la ampliación es sumamente necesaria; si no, fraccionar
ampliacion_justificacion: ""       # R-21: qué se rompe si se entrega en partes de ≤5 archivos
ampliacion_aprobada_at: null       # R-21: lo fija la aprobación humana; sin él no se ejecuta la ampliación
fraccion_de: null                  # R-21: id de la instrucción plan, si esta es una fracción
depende_de: []                     # R-21: fracciones que deben cerrarse antes
related_audits: []
related_endpoints: []
---

<!-- Ubicación (R-17): 05-instrucciones/01-pendientes/YYYY-MM-DD/ (fecha = created). Al aprobar → 02-en-progreso/; al cerrar → 03-completadas/. -->

# YYYYMMDD-NNN — Título corto

> **Contrato IA:** frontmatter + secciones hasta **Decisión a tomar**. El **Anexo** es checklist humano/PR — la IA solo lo consulta al **cerrar** (`status: done`).

## Pedido (síntesis)

- Máx. 3–5 viñetas.

## Objetivo

Una frase: qué quedará verdadero al terminar.

## Vínculos del acto

- **Entrada:** (por qué existe esta instrucción; 1–3 enlaces — `vinculos_entrada`)
- **Contexto mínimo:** (debe coincidir con `lectura_minima` abajo)
- **Salida esperada:** (operativa + espejo + colas 45/46 — rellenar `vinculos_salida` al cerrar)

Ver [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md).

## Lectura mínima (IA)

Lista cerrada — marcar al leer; **no abrir otros docs**:

- [ ] `docs/25-areas/<area>/CONTEXTO.md`
- [ ] (añadir solo fichas/ADRs necesarios)

No incluir espejo salvo `espejo_leer`. Guía humana: [redaccion-lectura-minima.md](../10-guias/redaccion-lectura-minima.md).

## Anclas de código

- `ruta/archivo.ts` — motivo en pocas palabras
- `ruta/otro.ts:40-80` — rango si el archivo es grande

Debe coincidir con `anclas_codigo` del frontmatter.

## Derivar espejo_actualizar

Regla: por cada ancla de código, añadir el path espejo 1:1 bajo `docs/50-sistema-integral/`:

| Regla | Espejo |
|-------|--------|
| `src/.../carpeta/` (nueva) | `docs/50-sistema-integral/src/.../carpeta/README.md` |
| `src/.../archivo.ts` | `docs/50-sistema-integral/src/.../archivo.md` |
| Cambio solo en README de carpeta | Actualizar `README.md` del espejo |

Copiar paths resultantes al frontmatter `espejo_actualizar`:

| Código (ancla) | Espejo (.md) |
|----------------|--------------|
| | |
| | |

## Alcance

- Incluye: …
- Excluye: …
- Repos / módulos: …

### Archivos de código (R-21)

- Total: N (estándar ≤5).
- Si N > 5 — **¿es sumamente necesaria la ampliación?** ¿Existe un subconjunto de ≤5 archivos entregable solo, compilando, con pruebas en verde y sin contratos rotos?
  - **Sí existe → no es necesaria:** fraccionar. Esta ficha pasa a plan y se crean hijas de ≤5 (`fraccion_de`, `depende_de`); una línea por hija en el plan.
  - **No existe → es necesaria:** `ampliacion_factor` (1.5–2, tope 7–10), `ampliacion_justificacion` y cada archivo extra con su motivo:
    - `ruta/archivo6` — motivo
- Guía: [ampliacion-alcance.md](../00-nucleo/ampliacion-alcance.md).

## Plan de ejecución (aprobar antes de codear)

1. …
2. Implementar código según anclas.
3. Sync operativa (CONTEXTO, `15-rutas/`, índices).
4. Sync espejo: paths en `espejo_actualizar`.
5. Cerrar con Resultado.

## Criterios de aceptación

- [ ] Código y tests según alcance
- [ ] Docs operativas actualizadas
- [ ] Espejo alineado con código tocado (`espejo_actualizar` completo)
- [ ] Reglas del proyecto revisadas (`96-reglas-proyecto/INDICE.md`); excepciones declaradas en `excepciones_reglas`
- [ ] Idioma (R-22): identificadores, archivos, tests, commits y rama nuevos en inglés y ASCII; términos locales en el glosario de dominio; texto para el usuario en i18n ([política](../00-nucleo/politica-idioma.md))
- [ ] Nombres (R-23): cada identificador nuevo o tocado se entiende sin comentario (intención, dominio, unidad); sin constantes mágicas; comentarios solo para el porqué ([guía](../00-nucleo/nombres-autoexplicativos.md))
- [ ] Sin pegar código en `.md` del espejo

## Riesgos / no tocar

…

## Decisión a tomar

> Solo cuando `status: awaiting_approval`. El revisor humano elige antes de ejecutar.

<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** — cambiar a `status: approved`, fijar `approved_at` y mover a `02-en-progreso/` (si declara `ampliacion_factor`, aprobar autoriza esa ampliación de alcance: R-21)
- [ ] <!-- decision:cancelar --> **Cancelar** — cambiar a `status: cancelled` y mover a `05-canceladas/`

## Resultado (al cerrar, status: done)

- Commits / PRs:
- Docs operativas actualizadas:
- Espejo actualizado (`espejo_actualizar`):
- Propuestas de herramienta (`herramientas_propuestas`):
- Mejoras registradas fuera de alcance (`mejoras_propuestas`):
- Evolución documental (`evolucion_documentacion`):
- Vínculos de salida (`vinculos_salida`):
- Movimiento: `03-completadas/YYYY-MM-DD/` (R-17)
- Notas:

---

## Costo en tokens

> Automático: `decisiones.py new` abre «Creación de la instrucción», `contexto.py` abre «Implementación» y `decisiones.py cerrar` escribe aquí la tabla por fases (análisis, instrucción, implementación, verificación, cierre) con el total. El agente marca `verificacion` y `cierre` al empezarlas: `python3 docs/scripts/costo-tokens.py fase <id> <fase>`. Guía: [costo-tokens.md](../10-guias/costo-tokens.md).

<!-- tokens:inicio -->
Pendiente: se mide al cerrar la instrucción.
<!-- tokens:fin -->

---

## Anexo — Checklist humano / PR

> **IA:** no leer esta sección durante planificación ni implementación; solo al cerrar la instrucción.

### Sync documental

| Capa | Qué actualizar | Paths |
|------|----------------|-------|
| Operativa | CONTEXTO / ficha / ADR / índice | … |
| Espejo | `50-sistema-integral/` | Ver abajo |

### Espejo integral

| Código | Espejo (.md) |
|--------|--------------|
| `src/modules/<id>/…` | `docs/50-sistema-integral/src/modules/<id>/README.md` |
| `src/modules/<id>/<archivo>.ts` | `docs/50-sistema-integral/src/modules/<id>/<archivo>.md` |

- [ ] `docs/50-sistema-integral/.../README.md` — crear o actualizar
- [ ] `docs/50-sistema-integral/.../<archivo>.md` — si aplica

### Registro de cobertura (si política incremental activa)

Si [`registro-cobertura-espejo.md`](../50-sistema-integral/registro-cobertura-espejo.md) indica **Política incremental: activa** y `espejo_actualizar` no está vacío al cerrar:

- [ ] Añadir fila al **Historial** con este `id` y los paths escritos
- [ ] Actualizar tabla **Cobertura por raíz**
- [ ] Quitar de **Huecos conocidos** los paths cerrados

### Propuesta de herramienta (opcional)

- [ ] Ficha en `docs/35-herramientas/propuestas/01-pendientes/YYYY-MM-DD/` + `herramientas_propuestas` — no implementar hasta promoción

### Mejora / deuda fuera de alcance (opcional)

- [ ] Ficha en `docs/45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/` + `mejoras_propuestas` (máx. 3; bugs con `tipo: bug`)

Ver [mejoras-propuestas-ia.md](../10-guias/mejoras-propuestas-ia.md).

### Evolución documental / cobertura pack (opcional)

- [ ] Ficha en `docs/46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` + `evolucion_documentacion` (máx. 2; solo sistema documental completo — R-18)
- [ ] Actualizar [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md)

Ver [_PROTOCOLO 46](../46-evolucion-documentacion/_PROTOCOLO.md).
