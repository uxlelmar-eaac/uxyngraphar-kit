# Reglas — servidor

Resumen de bajo costo para IA. Detalle: [AGENTES.md](../AGENTES.md) · [00-nucleo/eficiencia-ia.md](00-nucleo/eficiencia-ia.md). Ante conflicto, **jerarquía normativa**: instrucción approved > PROTOCOLO.md > _PROTOCOLO de carpeta > convenciones-frontmatter > ADR aceptada > guías y manuales > plantillas; si este resumen contradice a un nivel superior, gana el superior y se registra una ficha EVO-*.

## Tokens / lectura

1. Solo `AGENTES.md` al entrar; luego instrucción aprobada.
2. Abrir **únicamente** paths en `lectura_minima` + anclas + `espejo_leer` (default vacío).
3. Máx. ~8 docs y ~5 archivos de código por tarea (default, R-06). Más de 5 archivos de código → R-21 (abajo).
4. Plan en instrucción → aprobación → codear → **escribir** `espejo_actualizar`.

## Código y docs

- Sin `approved` → no editar código ni docs.
- CONTEXTO + fichas citadas; no índices enteros ni `90-archivo/`.
- Ruta nueva → ficha + índices + espejo incremental.
- Espejo: referencia visual; no leer salvo cita en instrucción.
- Herramienta autorizada: excepción — solo ficha + anclas (R-08); no propuestas.
- **Límite 350 líneas (R-19):** ningún archivo de código supera 350 líneas físicas (`wc -l`); proyecto nuevo = bloqueante; proyecto existente = inventario en `40-auditorias/` + fichas `MEJ-*` en 45 y ajuste progresivo; toda división con nomenclatura relacional. Detalle: [limite-350-lineas.md](00-nucleo/limite-350-lineas.md).

## Alcance de código > 5 archivos (R-21)

1. Antes de editar, evaluar y **justificar en `Alcance`** si la ampliación es sumamente necesaria: ¿hay un subconjunto de ≤5 archivos entregable solo, compilando y sin contratos rotos?
2. **No es necesaria** → fraccionar en instrucciones hijas de ≤5 (`fraccion_de`, `depende_de`), entregables por separado; nunca exceder el estándar.
3. **Es necesaria** → `ampliacion_factor` 1.5–2 (tope 7–10, nunca más) + `ampliacion_justificacion`; **aprobación humana explícita antes de proceder** (`ampliacion_aprobada_at`).
4. Detalle: [ampliacion-alcance.md](00-nucleo/ampliacion-alcance.md).

## Idioma del código del producto (R-22)

1. Código, archivos, tests, commits, ramas, logs, esquemas y contratos del producto → **inglés y ASCII**, aunque el pedido venga en español. Conversación con el humano → su idioma. `docs/` no entra.
2. Término local sin equivalente → solo si está en `00-nucleo/glosario-dominio.md` (ASCII, sin conjugar ni pluralizar). Campos de contratos externos (p. ej. CFDI) → tal cual en el adaptador, registrados en el glosario.
3. Commits: `tipo(alcance): description` (Conventional Commits). Ramas: `tipo/alcance-descripcion`.
4. Errores para consumidores de la API → código estable en inglés (`payment.declined`); el cliente traduce. Correos y notificaciones → plantillas por idioma.
5. Legacy: no renombrar en masa; solo si todos los usos están en `anclas_codigo` (si no → ficha en 45); contratos públicos → ADR + migración.
6. Detalle y configuración (`idioma` en `uxyngraphar.config.json`): [politica-idioma.md](00-nucleo/politica-idioma.md).

## Nombres autoexplicativos (R-23)

1. El nombre dice **qué es, para qué existe y cómo se usa**; si necesita un comentario que explique el *qué*, renombrar. Comentarios solo para el **porqué** (regla de negocio no obvia).
2. Intención, no implementación (`SECONDS_PER_DAY`, no `d`); unidad o contexto (`timeoutMs`, `weightKg`); nada de `data`, `info`, `value`, `temp`, `flag`, `x`.
3. Vocabulario del dominio, en inglés salvo términos del glosario de dominio (R-22); un concepto = un nombre en todo el proyecto.
4. Por rol: sustantivos para datos, verbos para funciones, predicados para booleanos (`isActive`, `canRetry`); sin prefijos de tipo ni abreviaturas no universales (`url`, `id`, `http` sí).
5. Literales con significado de negocio → constante con nombre (`ORDER_STATUS.SHIPPED`, no `3`).
6. Excepciones: `i`/`j` en bucles cortos, `x`/`y`/`n` matemáticos, lambdas de una línea, nombres de APIs externas, locales de alcance mínimo.
7. Detalle y checklist de revisión: [nombres-autoexplicativos.md](00-nucleo/nombres-autoexplicativos.md).

## Obligatorio al cerrar / revisar

- Mejora fuera de alcance → ficha en `45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/` (≤3; bugs con `tipo: bug`); gap del **sistema documental completo** → ficha en `46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` (≤2). No implementar en el mismo PR.
- 46 es **solo** evolución del sistema documental completo (R-18); la documentación funcional del proyecto nunca se crea ni se mueve a 46.
- Revisión de pendientes (humano): bandejas MEJ, EVO, instrucciones y propuestas vía [`decisiones-pendientes`](35-herramientas/autorizadas/decisiones-pendientes.md).
- Estados (R-17): al cambiar `status`, mover el archivo a la carpeta de estado correspondiente (conservando `YYYY-MM-DD` de creación); al cerrar, instrucción → `03-completadas/`.
- Estado inicial (R-16): bloque **Decisión a tomar** ⇒ decisión abierta y efecto **no** aplicado. Si el humano ya decidió, la ficha se emite en estado final, sin bloque y con sección `Aprobación`. Prohibido «aplicado + pendiente».
- Secretos: solo placeholders (`<API_KEY>`, `<DATABASE_URL>`); revisar espejo y fichas `15-rutas/` en cada PR. `controlar.py` bloquea credenciales y archivos de llaves/`.env` en cada commit y PR.

## Núcleo inviolable (R-20)

1. El núcleo solo cambia en el repo fuente de uxyngraphar; en el proyecto entra solo con `actualizar-pack.py` (humano).
2. No editar, borrar, renombrar ni crear archivos en zonas de núcleo (lista en [AGENTES.md](../AGENTES.md)); tampoco `.uxyngraphar.lock`, `.claude/settings.json`, `CODEOWNERS`, CI ni ganchos git.
3. Mejora al sistema → solo ficha `EVO-*` en `46-evolucion-documentacion/` (buzón hacia el pack). Nunca aplicarla.
4. No saltarse la verificación (`--no-verify`, `--warn`, desactivar ganchos o CI).
5. Núcleo alterado o `doctor.py` en rojo → parar y avisar al humano; no reparar a mano.

## Prohibido

- Leer `INDICE.md`, `PROTOCOLO.md` o `10-guias/` en tareas normales (salvo acto `adoptar` o cita en instrucción).
- Volcar `docs/` o espejo completo; explorar repo sin anclas.
- Escribir en `autorizadas/`; ejecutar `propuestas/`.
- Documentar fuera de instrucción aprobada (salvo excepciones PROTOCOLO).
- Implementar items de 45/46 sin instrucción derivada; modificar taxonomía o plantillas inline.
- Crear/renombrar carpetas `00`–`90` o mover contenido 45↔46↔35 sin `EVO-*` aprobado (R-14).
- Mover archivos entre carpetas de estado sin actualizar `status` en frontmatter (R-17).
- Mover o crear documentación funcional del proyecto en `46-evolucion-documentacion/` (R-18).
- Crear o modificar archivos de código superando 350 líneas físicas sin dividir con nomenclatura relacional (R-19).
- Tocar más de 5 archivos de código sin fraccionar ni ampliación aprobada, o ampliar más de 2× (R-21).
- Escribir código, archivos, commits o ramas del producto en otro idioma que no sea inglés, con caracteres no-ASCII o con idiomas mezclados (R-22).
- Nombres genéricos o abreviados (`data`, `tmp`, `mgr`), constantes mágicas o comentarios que expliquen el *qué* en lugar de renombrar (R-23).
- Leer, buscar o ejecutar algo en `95-memoria/`, o citarla por ruta (R-24); si una tarea la necesita, pedirlo en la instrucción.
- Editar el núcleo para aplicar una mejora en local, o crear, editar o retirar ajustes de `97-ajustes-locales/`, o activar o ejecutar el envío de sugerencias (`feedback.py`) o responder la pregunta de colaboración: es decisión humana (R-25).
