# Costo en tokens por instrucción

Cada instrucción termina con una tabla de cuántos tokens costó, separada por fases, y un total. Sirve para comparar instrucciones, ver qué fase pesa más y ajustar plantillas y presupuestos. Se mide en tokens, no en dinero.

## Fases

| Fase | Desde | Hasta |
|------|-------|-------|
| Análisis | inicio de la sesión (o cierre de la instrucción anterior) | se crea la ficha |
| Creación de la instrucción | `decisiones.py new instruccion` (automático) | se pide el contexto |
| Implementación | `contexto.py <id>` (automático) | marca de verificación |
| Verificación | `costo-tokens.py fase <id> verificacion` (pruebas, `controlar.py`, validadores) | marca de cierre |
| Cierre | `costo-tokens.py fase <id> cierre` (espejo, docs, fichas 45/46) | `decisiones.py cerrar <id>` (automático: escribe la tabla) |

Se puede volver a una fase (p. ej. de verificación a implementación marcando `implementacion` otra vez): se suman todos sus tramos. La espera por la aprobación humana no consume tokens.

## Qué mide cada columna

`Entrada` (tokens nuevos enviados) · `Caché leída` (contexto reutilizado; suele ser la mayor y la más barata) · `Caché escrita` · `Salida` (lo que escribe el agente) · `Total` y `%` del total. Debajo: **tokens nuevos** (total sin caché leída), la fuente y la fecha.

## De dónde salen los números

1. **Medido** (preferido): `usage` real de cada respuesta en las transcripciones de Claude Code (`~/.claude/projects/`, o `$CLAUDE_CONFIG_DIR/projects`), solo las de sesiones cuyo directorio está dentro del repo. Incluye subagentes. Otra ubicación: `--transcripciones DIR` o `UXYNGRAPHAR_TRANSCRIPCIONES`.
2. **Manual**: para herramientas que muestran su consumo: `costo-tokens.py registrar <id> <fase> --entrada N --salida N [--cache-lectura N] [--cache-escritura N]`.
3. **Estimado**: si no hay nada de lo anterior, ~4 caracteres/token de la ficha y del contexto leído. Es solo orientativo (no incluye razonamiento ni salida real) y la tabla lo indica.

## Comandos

```bash
python3 docs/scripts/costo-tokens.py fase <id> verificacion     # el agente, al empezar a verificar
python3 docs/scripts/costo-tokens.py fase <id> cierre           # el agente, al empezar el cierre
python3 docs/scripts/costo-tokens.py ver <id>                   # cómo va (no escribe)
python3 docs/scripts/costo-tokens.py medir <id>                 # reescribe la tabla (p. ej. tras registrar a mano)
python3 docs/scripts/costo-tokens.py resumen [--json]           # todas las medidas y la media por fase
```

Las marcas viven en `docs/.decisiones/tokens/` (fuera de git). La tabla queda en la ficha, entre `<!-- tokens:inicio -->` y `<!-- tokens:fin -->`, con los datos en un comentario para `resumen`. No editar la tabla a mano.

Relacionado: [eficiencia-ia.md](../00-nucleo/eficiencia-ia.md) (cómo gastar menos) · `presupuesto.py` (cuánto pesa leer algo antes de hacerlo).
