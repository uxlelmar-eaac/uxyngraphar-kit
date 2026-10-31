---
id: decisiones-pendientes
status: authorized
source: human
authorized_by: pack-documentacion
authorized_at: 2026-08-08
scope: [documentacion, revision-pendientes]
anclas_codigo:
  - scripts/decisiones/decisiones.py
  - scripts/decisiones/scanner.py
  - scripts/decisiones/applier.py
  - scripts/decisiones/applier_rutas.py
  - scripts/decisiones/session_acciones.py
presupuesto_max_docs: 2
lectura_minima:
  - docs/00-nucleo/convenciones-frontmatter.md
---

# Revisión de pendientes (decisiones-pendientes)

> Herramienta autorizada para **revisar y decidir** todo lo que quedó pendiente: instrucciones sin aprobar, mejoras (45), evolución del pack (46), propuestas de herramientas y promociones de auditorías. Ejecutable sin instrucción nueva cuando el pedido humano es revisar o registrar decisiones pendientes en la documentación.

## Qué hace

Consolida en un único listado las **decisiones a tomar** dispersas en instrucciones (`awaiting_approval`), propuestas de herramientas (`pending`), mejoras propuestas (`45`), evolución documental (`46`), ADRs en `propuesta` y promociones de auditorías activas.

- **Escaneo:** detecta fichas pendientes por frontmatter y bloques `<!-- decision-group: ... -->` (alias sección **Decisión humana**), en todas las carpetas de estado (`01-pendientes` …).
- **Registro:** el subcomando `register` guarda la elección en `.decisiones/sesion-activa.json` (sesión activa).
- **Aplicación:** escribe al `.md` origen (status, checkbox, nota en **Notas del humano**).
- **Post-decisión:** mueve la ficha a la **carpeta de estado** correspondiente (R-17) conservando su carpeta de fecha: rechazadas/canceladas → `05-canceladas/`, aprobadas → `02-en-progreso/` (o `03-completadas/` según tipo), borrador en `autorizadas/` al promover, placeholder `instruction_derivada` al aprobar mejora/EVO.

## Cuándo usar

- Revisión humana de propuestas IA en `35-herramientas/propuestas/`, `45-mejoras-propuestas/` o `46-evolucion-documentacion/` (en sus carpetas de estado).
- Aprobar o cancelar instrucciones en `awaiting_approval` (`05-instrucciones/01-pendientes/`).
- Revisión de promociones pendientes en `40-auditorias/02-en-progreso/`.
- Revisión post-PR de pendientes antes de promover fichas a `autorizadas/` o crear instrucción derivada.

**No usar si:** el cambio es implementación de producto → crear instrucción normal.

## Cómo ejecutar

Desde la **raíz del repositorio** (donde `docs/` contiene el pack):

> (En Windows: `py -3` en lugar de `python3`.)

```bash
python3 docs/scripts/decisiones/decisiones.py scan
python3 docs/scripts/decisiones/decisiones.py scan --max-days 30
python3 docs/scripts/decisiones/decisiones.py register --id MEJ-YYYYMMDD-slug --action aprobar
python3 docs/scripts/decisiones/decisiones.py apply --dry-run
python3 docs/scripts/decisiones/decisiones.py apply
python3 docs/scripts/decisiones/decisiones.py close-session
```

Herramientas adicionales (v2.2.0; todas de solo consola, stdlib):

```bash
# Métricas de colas, antigüedad y presupuesto (--json para CI)
python3 docs/scripts/decisiones/decisiones.py metricas [--json] [--max-days 30]
# Archivar completadas antiguas (03→04) y limpiar canceladas (05→06). Dry-run por defecto; nunca borra
python3 docs/scripts/decisiones/decisiones.py archivar --dias 90 [--apply]
python3 docs/scripts/decisiones/decisiones.py limpiar --dias 180 [--apply]
# Andamiaje de fichas desde plantilla (id correlativo, carpeta de estado/fecha y enlaces correctos)
python3 docs/scripts/decisiones/decisiones.py new {instruccion|mejora|evo|auditoria|propuesta|adr} --slug mi-slug
# Deriva del espejo en un PR (WARN; --strict o STRICT_ESPEJO=1 para fallar)
python3 docs/scripts/verificar-espejo.py --base origin/main
# Ganchos git opt-in (pre-commit; --pre-push opcional; --quitar los elimina)
python3 docs/scripts/instalar-ganchos.py
# Cierre y estado
python3 docs/scripts/decisiones/decisiones.py cerrar <id> [--dry-run]    # done + mover a 03-completadas + enlaces
python3 docs/scripts/decisiones/decisiones.py estado --escribir          # actualiza el bloque autogenerado de docs/ESTADO.md
# Núcleo: instalar, actualizar (simula por defecto) y verificar integridad
python3 docs/scripts/instalar-pack.py RUTA/AL/PACK --repo .
python3 docs/scripts/actualizar-pack.py RUTA/AL/PACK [--apply]
python3 docs/scripts/verificar-nucleo.py
# Depuración del contenido (nunca toca el núcleo)
python3 docs/scripts/decisiones/decisiones.py depurar --plan plan.json            # informe + plan editable
python3 docs/scripts/decisiones/decisiones.py depurar --aplicar plan.json         # simula los ítems con "aprobado": true
python3 docs/scripts/decisiones/decisiones.py depurar --aplicar plan.json --apply
```

`depurar` diagnostica archivar/limpiar, fichas que ya tocan pasar a la memoria (en `06-listas-para-eliminar` o mucho tiempo en `04-archivadas`), anclas de código inexistentes y espejo huérfano, y reescribe los enlaces entrantes al mover. **Nada se borra (R-24):** la acción `memoria` guarda la ficha en `95-memoria/` y exige `motivo` en el plan, una persona en la terminal y que nada vivo la enlace. Los plazos salen de `uxyngraphar.config.json` → `memoria`. Consultar o recuperar: `scripts/memoria.py` ([10-guias/memoria.md](../../10-guias/memoria.md)). En un plan, la acción `eliminar` es sinónimo de `memoria`: tampoco borra.

La antigüedad para `archivar`/`limpiar` se mide por la carpeta de fecha (R-17). Las ADR no se archivan solas.

Validación documental (WARN por defecto; fallo con `STRICT_DECISIONES=1`):

```bash
STRICT_DECISIONES=1 DECISIONES_MAX_DAYS=30 python3 docs/scripts/validar-documentacion.py
```

### Multi-pack (servidor + cliente)

```bash
export DOCS_DIRS="/ruta/docs-backend,/ruta/docs-frontend"
python3 docs/scripts/decisiones/decisiones.py scan
```

### Variables de entorno

| Variable | Default | Uso |
|----------|---------|-----|
| `DOCS_DIR` | `docs` | Raíz del pack (si no se auto-detecta) |
| `DOCS_DIRS` | — | Lista separada por comas para escaneo multi-pack |
| `DECISIONES_USER` | usuario OS | Autor del registro en sesión |
| `STRICT_DECISIONES` | `0` | `1` = validar-documentacion.py falla si hay pendientes antiguas |
| `DECISIONES_MAX_DAYS` | `30` | Umbral de antigüedad en validación |
| `STRICT_VINCULOS` | `0` | `1` = **falla** si instrucciones `done` sin `acto`/`vinculos_salida` |
| `STRICT_PRESUPUESTO` | `0` | `1` = ERROR si `lectura_minima`+`espejo_leer` > `presupuesto_max_docs` |

## Alcance permitido (excepción sin instrucción)

- Escanear documentación y listar decisiones pendientes.
- Registrar decisiones humanas en sesión JSON e historial archivado.
- Aplicar sesión a fichas con bloques `decision-group` / frontmatter estándar.
- Mover fichas entre **carpetas de estado** (R-17), generar borrador en `autorizadas/`, marcar status y checkboxes.
- **No** implementar código de producto ni crear instrucciones derivadas completas (solo placeholder `instruction_derivada`).

## Riesgos / límites

- **Rutas:** `apply` solo escribe dentro de las raíces del pack (`DOCS_DIR`/`DOCS_DIRS`); una ruta absoluta, con `..` o que escape por enlace simbólico se rechaza con error.
- **Acciones:** cada tipo admite solo sus acciones (más `posponer`/`eliminar`); `register` con id inexistente o acción inválida sale con código 2 y `apply` sale con 1 si alguna decisión falla.
- **Auditorías:** `aprobar` (promover) cierra la auditoría (`cerrada`, `03-completadas/`); `rechazar` la cancela (`05-canceladas/`).
- **Ampliación de alcance (R-21):** las instrucciones que piden más de 5 archivos de código salen marcadas con `+` y su `context` (JSON) muestra factor, tope y justificación. Preséntalas al humano **con esa justificación** y pide confirmación explícita de la ampliación: aprobarlas fija `ampliacion_aprobada_at`. `apply` rechaza aprobar una instrucción con alcance mal declarado (más de 5 sin factor, factor fuera de 1.5–2, tope superado o sin justificación). Ver [ampliacion-alcance.md](../../00-nucleo/ampliacion-alcance.md).
- **Sesión:** `sesion-activa.json` se escribe de forma atómica, pero no hay bloqueo entre procesos: no ejecutar dos `register`/`apply` a la vez.
- Requiere **Python 3.10+** (stdlib; sin pip).
- Completar manualmente `instruction_derivada` y promover borrador a `status: authorized`.
- Ignorar `.decisiones/sesion-activa.json` en git — ver el `.gitignore` de la raíz del repo.

## Anclas

| Recurso | Path |
|---------|------|
| CLI | `scripts/decisiones/decisiones.py` |
| Scanner | `scripts/decisiones/scanner.py` |
| Applier | `scripts/decisiones/applier.py` |
| Convención | `00-nucleo/convenciones-frontmatter.md` |
