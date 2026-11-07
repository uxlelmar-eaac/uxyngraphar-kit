# Caso: prohibir `console.log` con una excepción para el arranque

## Pedido

«Quiero que nadie deje `console.log` en `src/`; usamos el logger. El único que se queda es el mensaje de arranque de `src/main.ts`.» Proyecto TypeScript sin reglas previas.

## Recorrido

**consultar-reglas.** `reglas.py indice` → `(sin reglas del proyecto activas)`. El pedido es fijar una regla: se salta a `proponer-cambios`.

**proponer-regla** (skill):

```
python3 $P/scripts/comun/fichas.py nueva regla --slug sin-console-log --titulo "Sin console.log en src"
```

Frontmatter rellenado:

```yaml
nivel: bloqueante
aplica_a:
  - src/**/*.ts
resumen: Sin console.log en src; usa el logger del módulo.
comprobacion_prohibido: "console\.log\("
```

Un primer intento con `"console\\.log\\("` hace que `verificar-reglas.py` avise: `comprobacion_prohibido: regex inválida (missing ), unterminated subpattern at position 15)`. Con una sola barra compila. Antes de activarla, `rg 'console\.log\(' src` da dos archivos: `src/orders/confirm-order.ts` y `src/main.ts`.

La persona la activa: `fichas.py estado REG-20261106-sin-console-log activa --humano`.

**verificar** (sobre todo el código, recién activada):

```
python3 $P/scripts/reglas.py comprobar
src/main.ts: REG-20261106-sin-console-log [bloqueante] línea 1 contiene lo prohibido (console\.log\()
src/orders/confirm-order.ts: REG-20261106-sin-console-log [bloqueante] línea 3 contiene lo prohibido (console\.log\()
reglas del proyecto: 2 incumplimientos, 2 bloqueantes
```

**proponer-excepcion** (skill) para el arranque:

```
python3 $P/scripts/comun/fichas.py nueva excepcion --slug log-de-arranque
```

Con `regla: REG-20261106-sin-console-log`, `archivos: [src/main.ts]` y el motivo («el logger aún no existe al arrancar»). La persona la aprueba con `fichas.py estado EXC-20261106-log-de-arranque aprobada --humano` y escribe `aprobada_por`.

**implementar.** En `confirm-order.ts`, `console.log("confirm")` pasa a `logger.info("order confirmed")`.

**verificar.**

```
python3 $P/scripts/reglas.py comprobar
src/main.ts: REG-20261106-sin-console-log [excepción aprobada] línea 1 contiene lo prohibido (console\.log\()
reglas del proyecto: 1 incumplimientos, 0 bloqueantes
```

`verificar-reglas.py` termina con `reglas-del-proyecto: 0 errores, 0 avisos`.

## Resultado

- Regla `REG-20261106-sin-console-log` activa y comprobada sin IA en cada verificación.
- Excepción aprobada y acotada a `src/main.ts`; cualquier `console.log` nuevo en otro archivo hace fallar la verificación.
- El agente no activó ni aprobó nada: propuso y la persona decidió.
