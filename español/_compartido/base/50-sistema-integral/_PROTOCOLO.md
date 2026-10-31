# Protocolo — espejo integral (servidor)

## Rol

`50-sistema-integral/` es un **espejo documental** del scaffolding del repo backend. La estructura de carpetas es **idéntica** a la del proyecto (desde las raíces declaradas en `configuracion-proyecto.md`). Solo existen archivos `.md`.

## Reglas duras

1. **Misma jerarquía** que el código: si existe `src/modules/auth/`, existe `docs/50-sistema-integral/src/modules/auth/`.
2. **Cero código** en el espejo: prohibido `.ts`, `.py`, `.go`, etc. Solo Markdown explicativo.
3. **Por cada carpeta** del espejo → al menos un `README.md` (usar [_PLANTILLA-README-carpeta.md](_PLANTILLA-README-carpeta.md)).
4. **Por cada archivo de código relevante** → opcional `<nombre-base>.md` junto al README (usar [_PLANTILLA-archivo.md](_PLANTILLA-archivo.md)). Ej.: `auth.service.ts` → `auth.service.md`.
5. **No duplicar** el contenido de `15-rutas/` ni pegar código; enlazar fichas e ids si aplica.
6. Archivos meta del pack (prefijo `_`, `INDICE.md`, `vision-espejo.md`) viven **solo en la raíz** de `50-sistema-integral/`, no dentro del espejo.

## Raíces y exclusiones

Definidas en `00-nucleo/configuracion-proyecto.md` → sección **Espejo integral**:

| Concepto | Ejemplo |
|----------|---------|
| Raíces a reflejar | `src/`, `prisma/`, `migrations/` |
| Excluir siempre | `node_modules/`, `dist/`, `build/`, `.git/`, `coverage/`, `docs/` |
| Excluir opcional | `test/fixtures/`, `**/*.spec.ts` (documentar carpeta `test/` con README, no cada spec) |

Al **resync**, crear carpetas nuevas del proyecto; no borrar `.md` existentes sin instrucción explícita.

## Nomenclatura

| En el repo | En el espejo |
|------------|--------------|
| `src/modules/auth/` | `50-sistema-integral/src/modules/auth/README.md` |
| `auth.controller.ts` | `auth.controller.md` (misma carpeta) |
| Carpeta vacía o solo config | `README.md` describiendo propósito |

Enlaces al código real: path relativo desde raíz del repo, p. ej. `` [`auth.service.ts`](../../../src/modules/auth/auth.service.ts) `` (ajustar `../` según profundidad).

## Multi-repo

- Este repo: espejo del **backend**.
- Repo cliente: espejo del **frontend** con la misma convención.
- [mapa-capas.md](mapa-capas.md) enlaza carpetas equivalentes entre repos (p. ej. dominio `auth` en ambos espejos).

## Mantenimiento

### Sync incremental (cada instrucción normal)

Toda instrucción `approved` que modifique código debe actualizar el espejo en el **mismo cierre** (campo `espejo_actualizar`):

| Evento en instrucción | Acción espejo |
|-----------------------|---------------|
| Carpeta nueva en código | Crear carpeta espejo + `README.md` |
| Archivo relevante nuevo | Crear `<nombre>.md` |
| Cambio de comportamiento | Actualizar `.md` afectado (editar **solo el bloque que cambia**, no reescribir la sección) |
| Refactor de ruta | Mover/renombrar `.md` (listado en alcance) |
| Typos sin cambio de rol | Opcional omitir (declarar en alcance) |

### Resync masivo

Solo vía instrucción `_PLANTILLA-generar-espejo-integral.md` (primera vez, proyecto pequeño o refactor grande).

### Acumulación incremental (proyectos medianos/grandes)

1. Aprobar una vez `_PLANTILLA-politica-espejo-incremental.md`.
2. Cada instrucción normal escribe paths en `espejo_actualizar`.
3. Mantener [`registro-cobertura-espejo.md`](registro-cobertura-espejo.md) al cerrar.
4. Doc general futura → `_PLANTILLA-consolidar-espejo-integral.md` (solo huecos).

Ver [espejo-incremental-proyectos-grandes.md](../10-guias/espejo-incremental-proyectos-grandes.md).

## Lectura IA

- **Escribir:** paths en `espejo_actualizar` al ejecutar.
- **Leer:** solo `espejo_leer` / `lectura_minima` (≤3). **Nunca** recorrer el espejo entero por defecto.

Ver [estrategia-instrucciones.md](../00-nucleo/estrategia-instrucciones.md).
