# PROTOCOLO — Documentación del cliente

## Taxonomía

| Tipo | Carpeta | IA por defecto | Presupuesto |
|------|---------|----------------|-------------|
| Núcleo | `00-nucleo/` | Solo si instrucción/CONTEXTO lo nombra | 0–2 archivos |
| Protocolo | este archivo + `*/_PROTOCOLO.md` | Al crear/cambiar docs | según necesidad |
| Instrucciones | `05-instrucciones/<estado>/YYYY-MM-DD/` | Solo la de la tarea | 1 |
| Guías | `10-guias/` | Onboarding / pruebas / API (no en tareas normales) | 0 |
| Rutas | `15-rutas/` | Citadas en CONTEXTO o `lectura_minima` | ≤3 |
| ADR | `20-decisiones/<estado>/YYYY-MM-DD/` | Del dominio, si citado | ≤1 |
| Áreas | `25-areas/` | CONTEXTO del área declarada | 1 |
| Manual | `30-manuales/` | Solo operaciones | 0 |
| **Herramientas** | `35-herramientas/` | Autorizadas: ficha citada o excepción; propuestas: humano revisa | ≤2 si autorizada |
| **Mejoras propuestas** | `45-mejoras-propuestas/<estado>/YYYY-MM-DD/` | **No leer** en tareas normales; escribir al cerrar instrucción (≤3) | 0 |
| **Evolución documental** | `46-evolucion-documentacion/<estado>/YYYY-MM-DD/` | **No leer** salvo revisión de pendientes/revisión cobertura; escribir al cerrar (≤2) | 0 |
| Auditoría | `40-auditorias/<estado>/YYYY-MM-DD/` | Solo `02-en-progreso` citadas | ≤1 |
| **Sistema integral** | `50-sistema-integral/` | Espejo 1:1; **lectura 0** default; escribir vía `espejo_actualizar` | ≤3 si `espejo_leer` |
| Archivo | `90-archivo/` | **Nunca** | 0 |
| **Memoria** | `95-memoria/` | **Nunca** (R-24): solo el humano, con `memoria.py` | 0 |
| **Ajustes locales** | `97-ajustes-locales/` | Solo el ajuste activo del archivo del núcleo que usas (R-25); `contexto.py` lo trae | ≤1 por archivo |

Secciones que acumulan documentos usan **estados + fechas** (R-17): `01-pendientes` … `06-listas-para-eliminar` con subcarpeta `YYYY-MM-DD` de creación. Detalle: [organizacion-estados-fechas.md](10-guias/organizacion-estados-fechas.md).

Ver [00-nucleo/eficiencia-ia.md](00-nucleo/eficiencia-ia.md).

## Reglas duras

1. **[R-01]** Si un doc no cambia una decisión o un procedimiento, no existe.
2. **[R-02]** **Endpoint nuevo = ficha nueva** en el mismo cambio/PR.
3. **[R-03]** **Orden humana de ejecución = instrucción `.md` antes de tocar código**; sin aprobación → no ejecutar.
4. **[R-04]** Capacitar a la IA vía `25-areas/<area>/CONTEXTO.md` + `lectura_minima` en instrucción; no volcar todo `docs/`.
5. **[R-05]** Hallazgos de auditoría que cambian reglas → **promoción** a canon / ADR / ficha (no dejar la verdad solo en la auditoría).
6. **[R-06]** Respetar presupuesto en [eficiencia-ia.md](00-nucleo/eficiencia-ia.md); ampliar solo con aprobación (archivos de código: R-21).
7. **[R-07]** **Documentación = instrucción:** crear o modificar docs (operativas o espejo) solo dentro de una instrucción `approved`; sync espejo vía `espejo_actualizar` al cerrar.
8. **[R-08]** **Herramientas autorizadas:** ficha en `35-herramientas/autorizadas/` con `status: authorized` + índice activo puede ejecutarse **sin instrucción nueva** (excepción); propuestas IA **nunca** se ejecutan hasta promoción.
9. **[R-09]** **Mejoras propuestas:** deuda técnica o refactor **fuera de alcance** → registrar en `45-mejoras-propuestas/` al cerrar instrucción; **nunca implementar** hasta instrucción derivada aprobada por humano.
10. **[R-10]** **Evolución documental:** gap del **pack** o cobertura general → registrar en `46-evolucion-documentacion/` al cerrar (≤2) o revisión de [`matriz-cobertura-proyectos.md`](46-evolucion-documentacion/matriz-cobertura-proyectos.md); **no confundir** con deuda de producto (45).
11. **[R-11]** **Ciclo vinculante:** todo acto del proyecto declara `acto` + `vinculos_*` en instrucción; enrutador en [ciclo-vinculante.md](00-nucleo/ciclo-vinculante.md).
12. **[R-12]** **Secretos:** prohibido tokens, keys o credenciales en docs; usar placeholders — ver [REGLAS.md](REGLAS.md).
13. **[R-13]** **Decisiones documentales:** fichas con sección **Decisión a tomar** (o alias **Decisión humana**) usan bloques `<!-- decision-group: <id> -->` + `<!-- decision:accion -->`. Revisión humana de pendientes → herramienta autorizada [`decisiones-pendientes`](35-herramientas/autorizadas/decisiones-pendientes.md). Convención: [convenciones-frontmatter.md](00-nucleo/convenciones-frontmatter.md).
14. **[R-14]** **Estructura del pack — intocable por IA:** sin instrucción `approved` derivada de `EVO-*`, prohibido crear/renombrar/eliminar carpetas numeradas (`00`–`90`), cambiar taxonomía o plantillas `_PLANTILLA*`, o mover contenido entre `45` ↔ `46` ↔ `35`. Gap del pack → ficha `EVO-*` + `evolucion_documentacion` (≤2). Verificado por `scripts/verificar-nucleo.py` (huellas en `.uxyngraphar.lock`); el núcleo solo cambia vía `actualizar-pack.py`.
15. **[R-15]** **Acto obligatorio:** sin `acto` válido y plantilla correspondiente ([ciclo-vinculante.md](00-nucleo/ciclo-vinculante.md)) → no ejecutar.
16. **[R-16]** **Estado inicial = estado real de la decisión.** Un bloque `Decisión a tomar` declara que la decisión **sigue abierta y su efecto NO está aplicado**. Por tanto: **(a)** si el humano ya decidió —en la instrucción `approved` o explícitamente en la sesión—, la ficha se emite **ya en su estado final** (`aceptada` / `approved` / `done`), **sin** bloque de decisión y citando en `Aprobación` quién decidió y cuándo; **(b)** si no hay decisión humana, se emite en su estado pendiente (`propuesta` / `pending`), **con** bloque, y su efecto **no se implementa** (R-03, R-09, R-10). **Prohibida la combinación «efecto ya aplicado + decisión pendiente»:** si aparece al cerrar, se ratifica o se revierte antes de cerrar. Detalle por tipo de ficha: [convenciones-frontmatter.md](00-nucleo/convenciones-frontmatter.md).
17. **[R-17]** **Organización por estados y fechas (obligatoria).** Toda sección que acumula documentos (`05-instrucciones`, `20-decisiones`, `40-auditorias`, `45-mejoras-propuestas`, `46-evolucion-documentacion`, `35-herramientas/propuestas`) se organiza en carpetas de estado `01-pendientes` | `02-en-progreso` | `03-completadas` | `04-archivadas` | `05-canceladas` | `06-listas-para-eliminar`, y dentro de cada estado en carpetas `YYYY-MM-DD` (fecha de creación). **Cambio de estado = mover el archivo** a la carpeta de estado correspondiente (conservando su carpeta de fecha) **y** actualizar `status` en frontmatter en el mismo acto. Fichas de colas se citan por `id`, no por ruta. Las secciones de referencia (`00`, `10`, `15`, `25`, `30`, `35/autorizadas`, `50`, `90`) no adoptan estados. Detalle: [organizacion-estados-fechas.md](10-guias/organizacion-estados-fechas.md).
18. **[R-18]** **Alcance de `46-evolucion-documentacion`.** Almacena **únicamente** propuestas, cambios y mejoras que afectan al **sistema documental completo** (arquitectura de documentación del ecosistema: pack, taxonomía, convenciones, plantillas, procesos, metodología). **Nunca** documentación funcional de un proyecto, módulo o feature (eso vive en 05, 15, 25, 45, 50…). **Prohibido** mover documentos de proyecto hacia `46` o generar documentación funcional dentro de `46`. Bugs → `45` (`tipo: bug`); investigaciones → `40`.
19. **[R-19]** **Límite 350 líneas por archivo de código.** Ningún archivo de código del sistema puede exceder **350 líneas físicas** (`wc -l`, con blancos y comentarios). Detalle y medición: [limite-350-lineas.md](00-nucleo/limite-350-lineas.md). **Proyecto nuevo:** regla estricta bloqueante — ningún archivo nuevo o modificado cierra instrucción superando el techo; PR con >350 = rechazado salvo excepción declarada en `restricciones.md`. **Proyecto ya elaborado:** inventario en auditoría `AUD-*-limite-350` (`40-auditorias/02-en-progreso/`) + fichas `MEJ-*` (`tipo: refactor`) en `45-mejoras-propuestas/01-pendientes/` (≤3 por cierre, R-09); ajuste solo vía instrucción derivada `approved`. **Toda división usa nomenclatura relacional** (`<raiz-original>.<relacion>.<ext>`, sufijos de capa; prohibido `*-parte2`, `*-nuevo`, `utils2`).
20. **[R-20]** **Núcleo inviolable en proyectos.** En un proyecto que usa uxyngraphar, el núcleo (clase N: `AGENTES.md`, `REGLAS.md`, `PROTOCOLO.md`, `00-nucleo/` salvo plantillas P, `10-guias/`, `55-automatizaciones/`, `scripts/`, `_PLANTILLA*`, `_PROTOCOLO*`) solo se modifica **en el repositorio fuente de uxyngraphar** y entra al proyecto únicamente con `scripts/actualizar-pack.py`. Ningún agente ni persona del proyecto lo edita, borra, renombra ni amplía; tampoco `.uxyngraphar.lock`, `.claude/settings.json`, `.github/CODEOWNERS`, `.github/workflows/`, ganchos git ni la verificación misma (`--no-verify`, `--warn`). Una mejora al sistema se registra solo como ficha `EVO-*` en `46-evolucion-documentacion/` (buzón hacia el pack). Verificación: `scripts/verificar-nucleo.py` y `scripts/doctor.py`. Núcleo alterado ⇒ no se repara a mano: se informa al humano, que restaura con `actualizar-pack.py --apply --restaurar-nucleo`.
21. **[R-21]** **Ampliación del alcance de archivos de código.** El estándar es **5 archivos de código** por instrucción (R-06). Si la tarea necesita más, el agente no edita nada y **primero evalúa si la ampliación es sumamente necesaria**: ¿existe un subconjunto de ≤5 archivos entregable solo, compilando, con pruebas en verde y sin contratos rotos? **(a) Sí → no es necesaria:** fraccionar en instrucciones hijas de ≤5 archivos (`fraccion_de`, `depende_de`), cada una entregable y cerrable sola, sin exceder el estándar. **(b) No → sí es necesaria:** declarar `ampliacion_factor` entre **1.5 y 2** (tope `floor(5 × factor)`: 7 a 10 archivos, nunca más) y `ampliacion_justificacion` (qué se rompe al entregar a medias), y esperar **aprobación humana explícita** (`ampliacion_aprobada_at`) **antes de proceder**. En ambos casos la justificación va en la sección `Alcance` de la ficha. Si ni con 2× alcanza, se fracciona en bloques de ≤10. Lo hacen cumplir `decisiones.py apply`, `contexto.py`, el validador, `controlar.py` y `decisiones.py cerrar`. Detalle: [ampliacion-alcance.md](00-nucleo/ampliacion-alcance.md).
22. **[R-22]** **Idioma del código del producto.** Código, identificadores, nombres de archivos y carpetas, tests, commits (Conventional Commits), ramas, PR, logs, errores técnicos, esquemas de BD, contratos de API, claves de configuración y comentarios del producto van **en inglés y en ASCII**, aunque el humano, el ticket o el legacy usen otro idioma; la **conversación** sigue el idioma del humano. `docs/` queda fuera (se escribe en el idioma del pack; el espejo cita identificadores tal cual). Única excepción: términos de dominio, nombres propios y campos de contratos externos registrados en [glosario-dominio.md](00-nucleo/glosario-dominio.md) (ASCII, sustantivo opaco). Texto para el usuario final → i18n con clave en inglés. Legacy: no renombrar en masa; renombrar en el mismo cambio solo si todos los usos están en `anclas_codigo` (si no → ficha en 45); contratos públicos → ADR + instrucción de migración. Parámetros en la sección `idioma` de `uxyngraphar.config.json`; lo hace cumplir `controlar.py` (`idioma`, `commits`, gancho `commit-msg`). Detalle: [politica-idioma.md](00-nucleo/politica-idioma.md).
23. **[R-23]** **Nombres autoexplicativos.** Todo identificador del producto (variable, constante, función, clase, tipo, archivo, test) explica por sí solo **qué representa, para qué existe y cómo se usa** en el dominio; si necesita un comentario que explique el *qué*, el nombre está incompleto. Los comentarios se reservan para el **porqué**. Nombrar por intención (no por implementación), con unidad o contexto (`timeoutMs`, `weightKg`), con vocabulario del dominio (en inglés salvo términos de [glosario-dominio.md](00-nucleo/glosario-dominio.md), R-22), diferenciado por rol (sustantivos, verbos, predicados booleanos; sin prefijos de tipo), sin abreviaturas no universales, sin constantes mágicas y con un nombre por concepto en todo el proyecto. Excepciones: índices de bucles cortos, convenciones matemáticas, lambdas de una línea, nombres impuestos por APIs externas, locales de alcance mínimo. Se verifica en code review («¿El nombre elimina la necesidad de un comentario?») y con los linters de nombres del lenguaje; sin control bloqueante. Detalle: [nombres-autoexplicativos.md](00-nucleo/nombres-autoexplicativos.md).
24. **[R-24]** **Memoria del sistema: nada se borra.** Las fichas que cumplieron su ciclo (en `04-archivadas` o `06-listas-para-eliminar`, y cualquiera que el humano decida) no se borran: pasan a `95-memoria/` con `scripts/memoria.py` (o `decisiones.py depurar`), que guarda la ficha tal cual, su huella en `catalogo.jsonl` y el motivo. La memoria **solo se añade** y **solo la consulta una persona** en la terminal (`buscar`, `ver`, `recuperar`, `purgar` para un dato sensible). **El agente no la lee, no la busca y no la cita por ruta**: si una tarea la necesita, lo pide en la instrucción y el humano decide. Lo hacen cumplir las reglas `deny`, `.cursorignore`/`.geminiignore`/`.aiexclude`, las herramientas del pack (que la ignoran), `controlar.py` (control `memoria`, bloqueante) y el CI. Detalle: [memoria.md](10-guias/memoria.md).
25. **[R-25]** **Ajustes locales y envío de sugerencias.** Una mejora del sistema documental (ficha `EVO-*` **aprobada**) puede aplicarse ya en el proyecto sin editar el núcleo: una persona crea con `scripts/ajustes.py` un ajuste en `97-ajustes-locales/` (contenido del proyecto, ninguna actualización lo toca) que dice qué archivo del núcleo complementa y guarda su huella. **El agente sigue el ajuste activo y, donde contradiga a ese archivo, manda el ajuste**; nunca crea, edita ni retira ajustes. `contexto.py` lo incluye tras el archivo citado; `ajustes.py verificar` y `doctor.py` avisan cuando una actualización cambia ese archivo o el CHANGELOG ya cita la EVO (entonces se retira). Enviar a quien mantiene uxyngraphar las fichas de 46 es **opcional y apagado por defecto**, y **solo salen fichas EVO** (nunca ajustes locales ni métricas de uso): solo lo activa una persona (nunca el agente), respondiendo «Sí» a la pregunta de colaboración al instalar o actualizar o con `scripts/feedback.py activar` (consentimiento explícito, registrado en `uxyngraphar.config.json`, que el agente no puede editar). Tras ese «Sí», las fichas EVO nuevas o cambiadas se envían cuando una persona ejecuta `instalar` o `actualizar` (o `feedback.py enviar`); **nunca desde CI, ganchos de git ni el agente**, y el agente no puede activar el envío, responder la pregunta ni ejecutarlo. Lo enviado sale sin nombre del proyecto, rutas, correos, enlaces ni credenciales. Detalle: [ajustes-locales.md](10-guias/ajustes-locales.md) · [envio-sugerencias.md](10-guias/envio-sugerencias.md).

## Jerarquía normativa (conflictos)

Ante contradicción entre documentos, el orden de precedencia es:

1. Instrucción `approved` de la tarea (contrato de lectura y alcance)
2. `PROTOCOLO.md` (este archivo, R-01–R-25)
3. `_PROTOCOLO.md` de la carpeta afectada
4. [convenciones-frontmatter.md](00-nucleo/convenciones-frontmatter.md) (campos, enums, ids)
5. ADR `aceptada` del dominio (prevalece sobre canon general en su ámbito)
6. Guías (`10-guias/`) y manuales (`30-manuales/`)
7. Plantillas (`_PLANTILLA*`)

`AGENTES.md` y `REGLAS.md` son resúmenes sin rango propio: si contradicen a un nivel superior, gana el nivel superior y la discrepancia se registra como ficha `EVO-*`. Impacto de cambios en el canon: [mapa-dependencias.md](00-nucleo/mapa-dependencias.md).

## Revisión de decisiones pendientes (humano)

| Acción | Herramienta |
|--------|-------------|
| Ver pendientes consolidadas | `python3 docs/scripts/decisiones/decisiones.py scan` |
| Registrar decisión | `python3 docs/scripts/decisiones/decisiones.py register --id <id> --action <acción>` |
| Validación CI opcional | `STRICT_DECISIONES=1 STRICT_VINCULOS=1 STRICT_PRESUPUESTO=1 python3 docs/scripts/validar-documentacion.py` — ver [ci-validacion-documentacion.md](10-guias/ci-validacion-documentacion.md) |

(En Windows: `py -3` en lugar de `python3`.)

No sustituye instrucciones `approved` para implementar producto; solo marca status/checkboxes y mueve fichas según alcance de la ficha autorizada.

## Zona horaria de nomenclatura

Fechas en **ids** de instrucción/auditoría: **UTC** (`YYYYMMDD`). Carpetas de fecha (estados): `YYYY-MM-DD` (fecha de creación, R-17).

## Secuencia de lectura del agente

0. **¿Es herramienta autorizada?** — Si el pedido humano coincide con ficha en `35-herramientas/autorizadas/` (`status: authorized`, en INDICE activo) → leer solo esa ficha + anclas; **sin instrucción nueva**. Si no → continuar.
1. `AGENTES.md` (raíz del repo) + `ESTADO.md` si existe
2. Instrucción aprobada vía `python3 docs/scripts/contexto.py <id>` (imprime ficha, lectura mínima y anclas) → campo `areas`
3. `25-areas/<area>/CONTEXTO.md`
4. Núcleo solo si CONTEXTO/instrucción lo exigen
5. Fichas `15-rutas/<area>/…` citadas
6. ADRs / auditorías `02-en-progreso` del área si aplican
7. Código ancla del CONTEXTO
8. Manual solo en operaciones

## Excepciones a la instrucción (sin crear instrucción)

- Erratas de una línea / renombrado trivial
- Preguntas de solo lectura
- Actualizar una instrucción ya aprobado cuando el humano lo pide explícitamente
- **Ejecutar herramienta** listada en `35-herramientas/autorizadas/` (`status: authorized`, pedido humano dentro del alcance de la ficha)
