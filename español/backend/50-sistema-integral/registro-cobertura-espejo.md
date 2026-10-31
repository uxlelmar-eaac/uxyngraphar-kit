# Registro de cobertura del espejo

Ledger **incremental**: qué partes del espejo ya existen gracias a instrucciones cerradas. Evita volcar todo el repo cuando se pide «documentación general del sistema».

## Estado del proyecto

| Campo | Valor |
|-------|-------|
| Política incremental | `no adoptada` → cambiar a `activa` tras aprobar [_PLANTILLA-politica-espejo-incremental.md](../05-instrucciones/_PLANTILLA-politica-espejo-incremental.md) |
| Estrategia recomendada | Proyecto pequeño: espejo masivo una vez. Mediano/grande: **incremental** + consolidar al final |
| Última actualización | — |
| Instrucciones que aportaron espejo | 0 |

## Cobertura por raíz (mantener al cerrar instrucciones)

Una fila por subárbol relevante bajo las raíces de [`configuracion-proyecto.md`](../00-nucleo/configuracion-proyecto.md).

| Raíz código | README espejo | Archivos `.md` (aprox.) | Última instrucción |
|-------------|---------------|---------------------------|-------------------|
| _(ej. `src/modules/auth/`)_ | — | — | — |

## Huecos conocidos (opcional, humano o consolidación)

Paths de código **sin** espejo aún — prioridad para [_PLANTILLA-consolidar-espejo-integral.md](../05-instrucciones/_PLANTILLA-consolidar-espejo-integral.md):

- _(vacío al inicio)_

## Historial (últimas 15 entradas)

| Instrucción `id` | Paths añadidos/actualizados en `50-sistema-integral/` |
|------------------|--------------------------------------------------------|
| — | — |

---

**Mantenimiento:** al cerrar cualquier instrucción con `espejo_actualizar` no vacío, la IA añade fila al historial y actualiza la tabla de cobertura. Ver [_PLANTILLA.md](../05-instrucciones/_PLANTILLA.md) → sección **Registro de cobertura**.
