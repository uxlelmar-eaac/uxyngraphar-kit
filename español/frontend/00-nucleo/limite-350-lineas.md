# Límite 350 líneas por archivo — pauta de modularidad (cliente)

Ningún archivo de código del sistema puede exceder **350 líneas físicas** (`wc -l`, incluye blancos y comentarios). Fin: sistema **mantenible, sostenible, escalable, modular y fácil de mantener y gestionar**.

Regla dura: [R-19](../PROTOCOLO.md). Resumen operativo: [restricciones.md](restricciones.md).

## Qué cuenta y qué no

- **Cuenta:** todo archivo de código fuente del sistema (componentes, hooks, `api/`, `reception/`, estilos hechos a mano, tests manuales, scripts: `.tsx`, `.ts`, `.js`, `.css`, etc.).
- **Medición:** `wc -l <archivo>` — 350 es el techo físico total, no solo LOC. No se descuentan blancos ni comentarios (si el archivo es ilegible con ellos, ya es señal de división).
- **Excepciones (únicas, declaradas):** generados (`generated/`, `*.generated.*`, tipos emitidos por OpenAPI), `lockfiles`, bundles/minificados (`*.min.js`, `.next/`, `dist/`), assets binarios. Toda excepción **debe declararse** en `restricciones.md` del proyecto; lo no declarado no es excepción.

## Proyecto que nace desde cero — regla estricta bloqueante

1. Ningún archivo nuevo o modificado puede cerrar una instrucción superando 350 líneas.
2. La IA verifica antes de implementar (anclas) y al cerrar (archivos tocados). Si el cambio previsto supera el techo, **divide primero** con nomenclatura relacional (ver abajo) dentro del mismo alcance.
3. Checklist de PR: `wc -l` sobre archivos tocados; >350 = PR rechazado salvo excepción declarada.

## Proyecto ya elaborado — inventario y ajuste progresivo

1. **Inventario (no bloquea):** al adoptar el pack o al abrir auditoría, la IA barre el repo (`wc -l`, excluyendo excepciones) y registra el resultado en una auditoría `40-auditorias/02-en-progreso/YYYY-MM-DD/AUD-YYYYMMDD-limite-350.md` con tabla `archivo | líneas | exceso | propuesta de división`.
2. **Bandeja de ajuste:** cada archivo o grupo relacional que exceda se registra como ficha `MEJ-*` en `45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/` (`tipo: refactor`, evidencia `path:línea`, líneas actuales). Máx. 3 por cierre de instrucción (R-09); el humano prioriza.
3. **Ajuste:** solo vía instrucción derivada `approved` (R-09). Cada refactor divide **con nomenclatura relacional** y actualiza CONTEXTO + fichas BFF + espejo (`espejo_actualizar`).
4. **Espejo:** la ficha espejo de cada archivo sobredimensionado lo señala en `Estado de tamaño` hasta quedar ≤350 (ver `_PLANTILLA-archivo.md`).

## Refactorización con nomenclatura relacional

Dividir no es picar el archivo en `parte1/parte2`. Es extraer por **relación** (responsabilidad, capa o dominio) y nombrar cada pieza conservando la **raíz del nombre original** + sufijo que declara la relación:

- **Patrón:** `<raiz-original>.<relacion>.<ext>` — la raíz mantiene el vínculo; el sufijo declara el rol.
- **Python (y lenguajes donde el `.` no puede ir en el nombre de archivo):** el separador es `_` → `<raiz>_<relacion>.py` (p. ej. `common_frontmatter.py`, `applier_promocion.py`). El `.` del patrón es sintaxis TS/JS: `common.estados.py` **no** es un módulo importable (`ModuleNotFoundError`). El módulo raíz (`common.py`) puede quedar como fachada que re-exporta las piezas, para no romper los imports existentes.
- **Sufijos por capa (cliente):** `.api` (transporte), `.mapper` / `.schema` (`reception/`), `.query` / `.mutation` (`hooks/`), `.dto` / `.view` (`types/`), `.integration` (frontera entre dominios), `.query-keys` (`model/`).
- **Ejemplo:** `RecursoList.tsx` (480 líneas) → `RecursoList.tsx` (UI fina) + `recurso.mapper.ts` + `use-recurso.query.ts` + `recurso.query-keys.ts` + `recurso.view.ts`. Cada pieza ≤350; la UI no importa red salvo por `hooks/` + `integrations/` según [arquitectura.md](arquitectura.md).
- **Prohibido:** `RecursoList-parte2.tsx`, `RecursoList-nuevo.tsx`, `utils2.ts` — nombres sin relación declarada.
- Cada división respeta `integrations/` como única frontera entre dominios y actualiza `docs/25-areas/<id>/CONTEXTO.md`.

## Verificación rápida

```bash
# Top archivos que exceden (excluye generados y dependencias)
find src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.css" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/dist/*" -not -path "*/generated/*" -exec wc -l {} + | sort -rn | awk '$1 > 350'
```
