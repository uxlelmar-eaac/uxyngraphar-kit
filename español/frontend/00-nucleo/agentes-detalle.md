# AGENTES — detalle (cliente)

Detalle completo de las reglas del agente. **No se carga por defecto**: `AGENTES.md` (raíz) es el punto de entrada compacto. Léelo solo si una instrucción lo cita o necesitas una regla concreta; solo lo que indique la instrucción aprobada (presupuesto abajo). (Compatibilidad: `AGENTS.md` en la raíz es un alias que apunta aquí.)

**Pedido humano vago:** redactar instrucción `awaiting_approval` (plantilla según `acto` en [ciclo-vinculante.md](ciclo-vinculante.md)) **antes** de leer más docs o codear.

## Presupuesto IA (obligatorio)

0. **¿Es herramienta autorizada?** — Si el pedido encaja con ficha en `docs/35-herramientas/autorizadas/` (`status: authorized`) → ejecutar excepción (solo ficha + anclas). Si no → pasos 0.5–3.
0.5. **Identificar acto** — Abrir solo [docs/00-nucleo/ciclo-vinculante.md](ciclo-vinculante.md) (enrutador) + instrucción o herramienta citada; no releer PROTOCOLO entero. Si existe `docs/ESTADO.md`, leerlo (1 archivo) para orientarse.
1. Seguir [docs/00-nucleo/eficiencia-ia.md](eficiencia-ia.md).
2. La instrucción aprobada define **lectura mínima** y **anclas**; no abrir nada más.
3. Planificar en la instrucción → aprobación → ejecutar.

## Antes de implementar

1. Orden de ejecución → instrucción en `docs/05-instrucciones/01-pendientes/YYYY-MM-DD/<slug>.md` + **aprobación** (R-17: al aprobar, mover a `02-en-progreso/` conservando la carpeta de fecha).
2. Sin `status: approved` → **no editar código**.
3. Campo `areas` de la instrucción → un `CONTEXTO.md` por área.

## Lectura acotada (máx. ~8 docs)

1. Instrucción de la tarea (no el historial).
2. Paths en `lectura_minima` del frontmatter.
3. Si tarea **mapa del repo / generar espejo** → leer solo paths en `espejo_leer` (≤3). **No leer espejo** en tareas normales de implementación.
4. Mapa de lectura del CONTEXTO.
5. Fichas `15-rutas/` citadas (solo BFF; API por **`id`**).
6. Código **solo** por `anclas_codigo` o anclas del CONTEXTO/ficha.
7. Auditoría: solo `40-auditorias/02-en-progreso/` si investiga.

## Ampliación del alcance de código (R-21)

El estándar es **5 archivos de código** por instrucción. Si el pedido necesita más, **antes de editar nada**:

1. **Evaluar la necesidad crítica** y escribir la justificación en `## Alcance`: ¿existe un subconjunto de ≤5 archivos que se pueda entregar solo, compilando, con pruebas en verde y sin romper contratos (API, esquema, IDs compartidos)?
2. **No es sumamente necesaria** (p. ej. dos módulos independientes, refactor adyacente, pruebas que pueden ir después) → convertir la instrucción en plan y **fraccionar** en hijas de ≤5 archivos con `fraccion_de` y `depende_de`; cada hija se entrega y se cierra sola. Nunca exceder el estándar.
3. **Es sumamente necesaria** (cambio de contrato o migración que a medias rompe el sistema) → declarar `ampliacion_factor` entre 1.5 y 2 (tope `floor(5 × factor)`: 7–10), `ampliacion_justificacion` y `presupuesto_max_archivos_codigo`; dejar la instrucción en `awaiting_approval` y **esperar la aprobación humana explícita** (`ampliacion_aprobada_at`). Sin ella `contexto.py` no entrega código.
4. Si ni con 2× alcanza → fraccionar en bloques de ≤10, cada uno con su propia ampliación.

Detalle: [ampliacion-alcance.md](ampliacion-alcance.md).

## Idioma del código del producto (R-22)

Conversación en el idioma del humano; **artefactos del producto en inglés y ASCII** (`docs/` queda fuera). Antes de entregar:

1. Identificadores, archivos, tests, commits y rama nuevos en inglés, sin acentos ni idiomas mezclados (`obtenerUserById` ✗ → `getUserById`).
2. Cada palabra no inglesa es un término de [glosario-dominio.md](glosario-dominio.md); si no, tradúcela o pide al humano que la registre. Contratos externos (CFDI, terceros): nombre original solo en el adaptador.
3. Texto para el usuario final por i18n (clave en inglés); logs y errores técnicos en inglés.
4. Legacy: renombra solo si todos los usos están en `anclas_codigo` y hay pruebas; si no, ficha en 45. Contratos públicos → ADR + migración.
5. Marca la casilla de R-22 en criterios de aceptación. `controlar.py` revisa lo nuevo (control `idioma`) y los commits (`commits`, gancho `commit-msg`).

Detalle: [politica-idioma.md](politica-idioma.md).

## Nombres autoexplicativos (R-23)

El nombre es la documentación primaria; el comentario, la excepción. Antes de entregar:

1. Cada identificador nuevo o tocado dice qué es, para qué existe y cómo se usa, sin leer su cuerpo ni un comentario (`calculateTotalPrice(basePrice, taxRate)`, no `calc(a, b)`).
2. Unidad o contexto cuando aporta (`timeoutMs`, `weightKg`); sin `data`, `info`, `value`, `temp`, `flag`, `x` ni abreviaturas no universales (`usr`, `cfg`, `mgr`).
3. Vocabulario del dominio (en inglés salvo glosario de dominio, R-22), un concepto = un nombre; sustantivos, verbos y predicados según el rol; constantes mágicas con nombre.
4. Prueba del comentario: si explica el *qué*, renombra; si explica el *porqué* (regla de negocio no obvia), se queda.
5. Marca la casilla de R-23 en criterios de aceptación. Renombrar legacy solo dentro de `anclas_codigo`; si no, ficha en 45.

Detalle: [nombres-autoexplicativos.md](nombres-autoexplicativos.md).

## Escritura documental (al cerrar)

- Sync operativa: CONTEXTO, BFF en `15-rutas/`, índices de registros.
- Sync espejo: paths en **`espejo_actualizar`** (obligatorio si hubo `anclas_codigo`).
- Instrucción cerrada: mover a `03-completadas/YYYY-MM-DD/` con `status: done` (R-17).

## Funcionalidad nueva

- BFF nuevo → ficha `15-rutas/` + índices + CONTEXTO.
- Módulo → `plantilla-modulo.md` + `25-areas/<id>/CONTEXTO.md`.
- Espejo → misma ruta bajo `50-sistema-integral/` + `README.md`.

## Núcleo de solo lectura (R-20)

El núcleo es **solo lectura para agentes**: `AGENTES.md`, `AGENTS.md`, `docs/REGLAS.md`, `docs/PROTOCOLO.md`, `docs/00-nucleo/` (salvo las plantillas que el proyecto rellena: `configuracion-proyecto`, `arquitectura`, `restricciones`, `registro-ids-compartidos`, `mapa-dependencias`), `docs/10-guias/`, `docs/55-automatizaciones/`, `docs/scripts/`, todo `_PLANTILLA*` y `_PROTOCOLO*`. No se editan, no se borran y **no se crean archivos nuevos dentro** de esas zonas. `verificar-nucleo.py` lo comprueba con huellas y `doctor.py` revisa todo el protocolo (R-20). Tampoco se tocan `.uxyngraphar.lock`, `.claude/settings.json`, `CODEOWNERS`, CI ni ganchos git, ni se evita la verificación. Si algo del núcleo aparece alterado, **detente y avisa al humano**: no lo repares a mano.

Para proponer una mejora al sistema hay **un único canal**: ficha `EVO-*` en `docs/46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` (usa `decisiones.py new evo --slug <slug>`). Nunca la apliques tú: el humano la aprueba y llega por `actualizar-pack.py`. No dejes propuestas en `README`, `45`, guías ni archivos sueltos de `docs/`.

## Límite 350 líneas por archivo (R-19)

Ningún archivo de código supera **350 líneas físicas** (`wc -l`). Proyecto nuevo: bloqueante — verificar anclas antes de codear y archivos tocados al cerrar; si el cambio supera el techo, dividir con nomenclatura relacional en el mismo alcance. Proyecto existente: inventariar en `40-auditorias/` (`AUD-*-limite-350`) y registrar `MEJ-*` (`tipo: refactor`) en 45 al cerrar (≤3); ajuste solo con instrucción derivada. Detalle: [limite-350-lineas.md](limite-350-lineas.md).

## Herramientas autorizadas (excepción)

Sin instrucción nueva: ejecutar solo si existe ficha en `docs/35-herramientas/autorizadas/<id>.md` con `status: authorized`, figura en `autorizadas/INDICE.md` y el pedido humano coincide con el **alcance permitido** de la ficha. Leer únicamente esa ficha (≤2 docs) + `anclas_codigo` de la ficha — regla [R-08](../PROTOCOLO.md).

**Revisión documental de pendientes (UI):** usar [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md) — `python3 docs/scripts/decisiones/decisiones.py scan` — para revisar pendientes en `45-mejoras-propuestas/`, `46-evolucion-documentacion/`, `35-herramientas/propuestas/` e instrucciones en `awaiting_approval`.

(En Windows: `py -3` en lugar de `python3`.)

## Propuestas IA

Crear en `docs/35-herramientas/propuestas/01-pendientes/YYYY-MM-DD/` solo dentro de instrucción o documentando en Resultado. Registrar paths en `herramientas_propuestas`. **Nunca ejecutar** código de una propuesta hasta promoción a `autorizadas/`.

## Mejoras / deuda fuera de alcance

Al **cerrar** instrucción: si detectas refactor o deuda **no pedida**, crear ficha en `docs/45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/` (máx. 3) y listar en `mejoras_propuestas`. **No implementar** en el mismo PR. Bugs detectados fuera de alcance → misma cola con `tipo: bug`.

Si detectas **gap del pack** o cobertura documental general (sistema documental completo, no docs de este proyecto), crear ficha en `docs/46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` (máx. 2) y listar en `evolucion_documentacion`. Ver [_PROTOCOLO 46](../46-evolucion-documentacion/_PROTOCOLO.md). **Nunca** mover documentación funcional del proyecto a `46` (R-18).

El humano revisa pendientes y crea instrucción derivada. Ver [mejoras-propuestas-ia.md](../10-guias/mejoras-propuestas-ia.md) · [ciclo-vinculante.md](ciclo-vinculante.md).

## Estructura del pack — intocable por IA

**Prohibido** sin instrucción `approved` derivada de `EVO-*`:

- Crear, renombrar o eliminar carpetas numeradas (`00`–`90`)
- Cambiar taxonomía, `PROTOCOLO.md` raíz o plantillas `_PLANTILLA*`
- Mover contenido entre `45` ↔ `46` ↔ `35`

**Obligatorio** al detectar gap del pack:

- Ficha `EVO-*` (`tipo`: `taxonomia` \| `plantilla` \| `proceso` \| `cobertura`)
- Path en `evolucion_documentacion` (máx. 2) + actualizar [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md)

## Generar documentación integral

Instrucción [`_PLANTILLA-generar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md): replicar estructura del frontend → solo `.md`. Sin aprobación → no generar espejo masivo.

## Canon (solo si la instrucción o CONTEXTO lo exigen)

- `docs/00-nucleo/configuracion-proyecto.md`
- `docs/00-nucleo/arquitectura.md` · `plantilla-modulo.md` · `restricciones.md` · `limite-350-lineas.md`

## Prohibido

- Leer `docs/INDICE.md`, `docs/PROTOCOLO.md` o `docs/10-guias/` en tareas normales (salvo acto `adoptar` o cita en instrucción).
- Volcar `docs/`, índices enteros o `90-archivo/`.
- Leer o listar masivamente `50-sistema-integral/` salvo `espejo_leer`.
- Código sin anclas declaradas.
- Documentar sin instrucción `approved` (salvo excepciones en PROTOCOLO).
- Duplicar fichas HTTP del servidor.
- Escribir en `35-herramientas/autorizadas/` (solo humano).
- Ejecutar propuestas en `35-herramientas/propuestas/`.
- **Implementar** mejoras listadas en `45-mejoras-propuestas/` o `46-evolucion-documentacion/` (solo registrar al cerrar).
- Crear o mover documentación **funcional del proyecto** dentro de `46-evolucion-documentacion/` (R-18: 46 es solo meta-sistema documental).
- Mover archivos entre carpetas de estado sin actualizar `status` (o viceversa) — R-17.
- Ejecutar sin `acto` válido + plantilla correspondiente ([ciclo-vinculante.md](ciclo-vinculante.md)).
- Refactor o deuda **fuera de alcance** en el PR actual (registrar en 45, no codear).
- **Secretos en docs:** tokens, API keys, passwords, `.env`, credenciales reales — usar `<PLACEHOLDER>` y referencias a gestor de secretos.
- Superar 350 líneas físicas por archivo o dividir sin nomenclatura relacional (R-19).
- Tocar más de 5 archivos de código sin fraccionar ni ampliación aprobada, o pedir más de 2× (R-21).
- Código, archivos, commits o ramas del producto fuera de inglés/ASCII o con idiomas mezclados (R-22).
- Nombres genéricos, abreviaturas no universales, constantes mágicas o comentarios que explican el *qué* en lugar de renombrar (R-23).

Operaciones → `docs/30-manuales/` únicamente en tareas ops.
