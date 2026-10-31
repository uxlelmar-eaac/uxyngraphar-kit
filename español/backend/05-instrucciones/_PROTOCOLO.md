# Protocolo de instrucciones

## Estructura (R-17)

```
05-instrucciones/
├── 01-pendientes/YYYY-MM-DD/<slug>.md   ← draft, awaiting_approval
├── 02-en-progreso/YYYY-MM-DD/<slug>.md  ← approved, executing
├── 03-completadas/YYYY-MM-DD/<slug>.md  ← done
├── 04-archivadas/YYYY-MM-DD/<slug>.md   ← archivada (humano, revisión periódica)
├── 05-canceladas/YYYY-MM-DD/<slug>.md   ← cancelled
└── 06-listas-para-eliminar/YYYY-MM-DD/  ← para-eliminar
```

- Archivo: `<slug>.md` (kebab, 2–6 palabras); `id` de frontmatter: `YYYYMMDD-NNN-slug` (fecha UTC).
- Carpeta de fecha = fecha de **creación**; se conserva al moverse de estado.
- **Cambio de estado = mover** a la carpeta de estado correspondiente + actualizar `status` en el mismo acto.
- Se cita por `id`; las rutas cambian con el estado.

## Ciclo

`draft` → `awaiting_approval` (01) → `approved` → `executing` (02) → `done` (03) | `cancelled` (05)

## Obligatorio (incl. eficiencia IA)

1. Crear instrucción **antes** de editar código o documentación (en `01-pendientes/YYYY-MM-DD/`).
2. Rellenar **`lectura_minima`**, **`anclas_codigo`**, **`espejo_actualizar`**, **`espejo_leer`**, **`acto`**, **`vinculos_entrada`** en frontmatter (listas cerradas).
3. Al aprobar: `status: approved` + `approved_at` + mover a `02-en-progreso/` (misma carpeta de fecha).
4. Al cerrar (`done`): rellenar **`vinculos_salida`** con ids y paths de docs tocados + mover a `03-completadas/`.
5. **`espejo_actualizar`:** obligatorio si `anclas_codigo` no está vacío (mapeo 1:1 a `docs/50-sistema-integral/...`). Typos sin cambio de rol → puede quedar `[]` (excepción documentada en alcance).
6. **`espejo_leer`:** default `[]`. Poblar solo si el humano pide consultar mapa existente (≤3 paths).
7. Plan en **Plan de ejecución**; estado `awaiting_approval` hasta OK humano.
8. Al cerrar: Resultado con docs operativas **y** espejo.
9. Respetar presupuestos; ampliar → aprobación.
10. **Más de 5 archivos de código (R-21):** evaluar primero si es sumamente necesario. No lo es → fraccionar en instrucciones hijas de ≤5 (`fraccion_de`, `depende_de`). Lo es → `ampliacion_factor` 1.5–2 (tope 7–10) + `ampliacion_justificacion`; aprobar fija `ampliacion_aprobada_at` y sin él no se ejecuta. Ver [ampliacion-alcance.md](../00-nucleo/ampliacion-alcance.md).
11. **Idioma (R-22):** el código del producto, sus archivos, commits y ramas van en inglés y ASCII aunque la instrucción esté en español; términos locales solo si están en el glosario de dominio; los archivos de locale se listan en `Alcance` pero no cuentan como archivos de código. Renombrar legacy solo si todos sus usos están en `anclas_codigo`. Ver [politica-idioma.md](../00-nucleo/politica-idioma.md).
12. **Nombres (R-23):** cada identificador nuevo o tocado explica qué es, para qué existe y cómo se usa sin comentario (intención, dominio, unidad); comentarios solo para el porqué; casilla de autochequeo en criterios de aceptación. Ver [nombres-autoexplicativos.md](../00-nucleo/nombres-autoexplicativos.md).

Enrutador de actos: [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md).

## Mapeo espejo (desde anclas)

```
src/modules/auth/auth.service.ts
  → docs/50-sistema-integral/src/modules/auth/auth.service.md
  → docs/50-sistema-integral/src/modules/auth/README.md (si la carpeta cambia)
```

Ver [estrategia-instrucciones.md](../00-nucleo/estrategia-instrucciones.md).

## Consumo

- Una sesión = **una** instrucción; no leer historial de `05-instrucciones/` (el árbol de estados es el índice).
- **No reabrir en la misma sesión**: documento ya abierto no se vuelve a abrir; si hace falta, citar de memoria de la sesión.
- Al cerrar (`done`): `vinculos_salida` con **máximo 10 líneas** (solo ids + paths + 1 línea por hallazgo clave). El cierre es el handoff a la siguiente tarea: pasar lo esencial, no el relato.
- Ver [00-nucleo/eficiencia-ia.md](../00-nucleo/eficiencia-ia.md).

## Excepciones (sin instrucción)

Erratas de una línea, solo lectura acotada, o actualizar instrucción ya aprobada a petición explícita.

## Plantillas especiales

Todas llevan **Contrato IA + Anexo** (mismo patrón que [_PLANTILLA.md](_PLANTILLA.md)): la IA ejecuta hasta **Decisión a tomar**; el **Anexo** es checklist humano/PR al cerrar.

Todas llevan `acto`, `vinculos_entrada` y, al cerrar, `vinculos_salida`:

| Plantilla | `acto` | Uso |
|-----------|--------|-----|
| [_PLANTILLA.md](_PLANTILLA.md) | `crear` / `editar` / `corregir` | Implementación + sync incremental espejo |
| [_PLANTILLA-solo-documentacion.md](_PLANTILLA-solo-documentacion.md) | `mejorar-docs` | Solo docs, sin código |
| [_PLANTILLA-adopcion-inicial-pack.md](_PLANTILLA-adopcion-inicial-pack.md) | `adoptar` | Primera adopción del pack |
| [_PLANTILLA-generar-espejo-integral.md](_PLANTILLA-generar-espejo-integral.md) | `crear` | Generación/resync masivo (proyecto pequeño o espejo vacío) |
| [_PLANTILLA-politica-espejo-incremental.md](_PLANTILLA-politica-espejo-incremental.md) | `adoptar` | **Una vez:** política incremental en proyectos medianos/grandes |
| [_PLANTILLA-consolidar-espejo-integral.md](_PLANTILLA-consolidar-espejo-integral.md) | `mejorar-docs` | Doc general del sistema — **solo huecos** (bajo coste tokens) |

## Propuestas de herramienta al cerrar

Si la tarea sugiere artefacto reutilizable:

1. Crear ficha en `35-herramientas/propuestas/01-pendientes/YYYY-MM-DD/` (`status: pending`, `source: ai`).
2. Añadir id a `herramientas_propuestas` en frontmatter y Resultado.
3. No implementar el código sugerido hasta promoción humana a `autorizadas/`.

## Archivo y eliminación

- `04-archivadas/`: el humano mueve ahí instrucciones `done` antiguas (p. ej. revisión trimestral) o pospuestas, con `status: archivada`.
- `06-listas-para-eliminar/`: humano mueve fichas candidatas a borrado; tras confirmación, se eliminan definitivamente.
