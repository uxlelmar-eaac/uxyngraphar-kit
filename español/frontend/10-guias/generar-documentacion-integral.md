# Generar documentación integral — espejo UI (cliente)

Guía para crear la documentación integral **copiando la estructura del frontend** y rellenándola solo con Markdown.

## Concepto

| Proyecto real | Documentación integral |
|---------------|------------------------|
| `src/app/dashboard/page.tsx` | `docs/50-sistema-integral/src/app/dashboard/page.md` |
| Misma carpeta `dashboard/` | `docs/50-sistema-integral/src/app/dashboard/README.md` |

No hay otra taxonomía: el espejo **es** el scaffolding UI, documentado.

## Pasos (humano)

### Proyecto pequeño o espejo vacío

1. Pegar el pack en `docs/` y rellenar [`00-nucleo/configuracion-proyecto.md`](../00-nucleo/configuracion-proyecto.md) → sección **Espejo integral** (raíces `src/app/`, etc.).
2. Copiar [`05-instrucciones/_PLANTILLA-generar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md) → `YYYYMMDD-NNN-generar-espejo.md`.
3. Completar raíces en `anclas_codigo` (p. ej. `src/app/`).
4. Aprobar la instrucción (`status: approved`).
5. La IA ejecuta el plan: recorre carpetas, crea espejo, escribe `.md` **sin tocar código**.

### Proyecto mediano, grande o muy grande (recomendado)

1. Rellenar `configuracion-proyecto.md` (raíces UI).
2. Aprobar **una vez** [`_PLANTILLA-politica-espejo-incremental.md`](../05-instrucciones/_PLANTILLA-politica-espejo-incremental.md).
3. En **cada** pantalla/BFF: [`_PLANTILLA.md`](../05-instrucciones/_PLANTILLA.md) + `espejo_actualizar`.
4. Doc general: [`_PLANTILLA-consolidar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-consolidar-espejo-integral.md).

Guía: [espejo-incremental-proyectos-grandes.md](espejo-incremental-proyectos-grandes.md).

## Qué escribe la IA

| En cada carpeta del espejo | Contenido |
|----------------------------|-----------|
| `README.md` | Propósito, tabla de hijos, enlaces al código real |
| `<archivo>.md` | Rol del `.tsx`/`.ts`/… equivalente (sin pegar código) |

Plantillas: [`_PLANTILLA-README-carpeta.md`](../50-sistema-integral/_PLANTILLA-README-carpeta.md), [`_PLANTILLA-archivo.md`](../50-sistema-integral/_PLANTILLA-archivo.md).

## Modos

| Modo | Cuándo |
|------|--------|
| **generar** | Primera vez; espejo vacío o parcial según registro |
| **resync** | Refactor: nuevas carpetas/archivos en código |
| **actualizar** | Cambio de comportamiento en paths concretos |

## Repo aislado vs multi-repo

| Escenario | Acción |
|-----------|--------|
| Frontend solo | Espejo UI; API por **id** en CONTEXTO |
| Monorepo | Ver [monorepo-docs-fusionados.md](monorepo-docs-fusionados.md) |
| Dos repos | [sync-multi-repo.md](sync-multi-repo.md) + [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md) |

Alinear features en [`mapa-capas.md`](../50-sistema-integral/mapa-capas.md).

## Errores comunes

- Inventar carpetas sueltas fuera del espejo 1:1 → **incorrecto**.
- Copiar código al espejo → **prohibido**.
- Duplicar fichas del backend → usar **id** en registro compartido.
- Leer todo el espejo en cada tarea IA → citar solo paths en `lectura_minima`.

Protocolo completo: [`50-sistema-integral/_PROTOCOLO.md`](../50-sistema-integral/_PROTOCOLO.md).
