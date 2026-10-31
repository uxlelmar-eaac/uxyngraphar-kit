# Generar documentación integral (espejo)

Guía para crear la documentación integral **copiando la estructura del proyecto** y rellenándola solo con Markdown.

## Concepto

| Proyecto real | Documentación integral |
|---------------|------------------------|
| `src/modules/auth/auth.service.ts` | `docs/50-sistema-integral/src/modules/auth/auth.service.md` |
| Misma carpeta `auth/` | `docs/50-sistema-integral/src/modules/auth/README.md` |

No hay otra taxonomía: el espejo **es** el scaffolding, documentado.

## Pasos (humano)

### Proyecto pequeño o espejo vacío

1. Pegar el pack en `docs/` y rellenar [`00-nucleo/configuracion-proyecto.md`](../00-nucleo/configuracion-proyecto.md) → sección **Espejo integral**.
2. Copiar [`05-instrucciones/_PLANTILLA-generar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md) → `YYYYMMDD-NNN-generar-espejo.md`.
3. Completar raíces en `anclas_codigo` (p. ej. `src/`).
4. Aprobar la instrucción (`status: approved`).
5. La IA ejecuta el plan: recorre carpetas, crea espejo, escribe `.md` **sin tocar código**.

### Proyecto mediano, grande o muy grande (recomendado)

1. Rellenar `configuracion-proyecto.md` (raíces del espejo).
2. Aprobar **una vez** [`_PLANTILLA-politica-espejo-incremental.md`](../05-instrucciones/_PLANTILLA-politica-espejo-incremental.md) → activa [`registro-cobertura-espejo.md`](../50-sistema-integral/registro-cobertura-espejo.md).
3. En **cada** feature: [`_PLANTILLA.md`](../05-instrucciones/_PLANTILLA.md) con `espejo_actualizar` al cerrar.
4. Cuando pidas doc general: [`_PLANTILLA-consolidar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-consolidar-espejo-integral.md) (solo huecos).

Guía: [espejo-incremental-proyectos-grandes.md](espejo-incremental-proyectos-grandes.md).

## Qué escribe la IA

| En cada carpeta del espejo | Contenido |
|----------------------------|-----------|
| `README.md` | Propósito, tabla de hijos, enlaces al código real |
| `<archivo>.md` | Rol del `.ts`/`.py`/… equivalente (sin pegar código) |

Plantillas: [`_PLANTILLA-README-carpeta.md`](../50-sistema-integral/_PLANTILLA-README-carpeta.md), [`_PLANTILLA-archivo.md`](../50-sistema-integral/_PLANTILLA-archivo.md).

## Modos

| Modo | Cuándo |
|------|--------|
| **generar** | Primera vez; espejo vacío o parcial según registro |
| **resync** | Refactor: nuevas carpetas/archivos en código |
| **actualizar** | Cambio de comportamiento en paths concretos |

## Multi-repo

Repetir en repo cliente con sus raíces (`src/app/`, etc.). Alinear features en [`mapa-capas.md`](../50-sistema-integral/mapa-capas.md).

## Errores comunes

- Inventar carpetas `dominios/` o `contratos/` sueltas → **incorrecto**; usar espejo 1:1.
- Copiar código al espejo → **prohibido**.
- Leer todo el espejo en cada tarea IA → citar solo paths en `lectura_minima`.

Protocolo completo: [`50-sistema-integral/_PROTOCOLO.md`](../50-sistema-integral/_PROTOCOLO.md).
