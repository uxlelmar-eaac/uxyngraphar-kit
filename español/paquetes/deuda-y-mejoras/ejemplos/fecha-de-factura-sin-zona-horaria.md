# Caso: un bug visto de pasada mientras se añade un campo

## Pedido

«Añade el campo `notas` al formulario de factura.» El proyecto tiene `deuda-y-mejoras` instalado. Mientras añade el campo, el agente ve en `src/invoices/format.ts:17` que la fecha de emisión se formatea con `new Date(fecha).toLocaleDateString()` sin zona horaria: una factura emitida a las 23:30 en México sale con fecha del día siguiente en el servidor (UTC). Arreglarlo es una línea. No se arregla.

## Recorrido

**clasificar-hallazgo.** El pedido es el campo `notas`; la fecha no forma parte de él. Es un bug del producto, no del sistema uxyngraphar, y no necesita investigación: es mejora a registrar. No es `critica` (no pierde datos), así que no hace falta avisar en el momento.

**buscar-duplicados.**

```
python3 $P/scripts/comun/fichas.py listar mejora --status pending
```

No devuelve nada, y `rg -l "invoices/format.ts" uxyngraphar/trabajo/deuda-y-mejoras/` tampoco: no hay ficha previa.

**registrar** (skill `registrar-mejora`):

```
python3 $P/scripts/comun/fichas.py nueva mejora --slug fechas-sin-zona-horaria --titulo "Fechas de factura sin zona horaria"
…/trabajo/deuda-y-mejoras/pendientes/MEJ-20261106-fechas-sin-zona-horaria.md
```

Se rellena:

```markdown
tipo: bug
severidad: media
prioridad: pronto
areas: [invoices]

## Contexto detectado
Al añadir el campo «notas» al formulario de factura se vio cómo se formatea la fecha de emisión.

## Evidencia
- `src/invoices/format.ts:17` — `toLocaleDateString()` sin `timeZone`: una factura de las 23:30 (UTC-6) sale con fecha del día siguiente en el servidor.

## Problema
La fecha impresa depende de la zona horaria del proceso, no de la del cliente.

## Mejora propuesta
Formatear con `Intl.DateTimeFormat` y la zona horaria de la empresa guardada en la configuración.

## Impacto si no se hace
Facturas con fecha incorrecta cerca de medianoche; posibles rechazos fiscales.
```

`verificar.py` sin errores. Es la primera ficha de la tarea (límite: 3). Al cerrar, el agente dice: «Añadí el campo `notas`. Además registré `MEJ-20261106-fechas-sin-zona-horaria` (bug de zona horaria en la fecha de factura); no lo he tocado.»

El agente no puede aprobarla:

```
python3 $P/scripts/comun/fichas.py estado MEJ-20261106-fechas-sin-zona-horaria approved
error: «approved» solo lo asigna una persona (usa --humano si eres tú)
```

**implementar-aprobada.** Días después la persona la aprueba con `--humano` y pide implementarla. El agente comprueba con `fichas.py ver` que está en `approved`, cambia solo el formateo de `format.ts` como dice la ficha y la pasa a `done`.

## Resultado

- El pedido (campo `notas`) quedó hecho sin cambios ajenos.
- El bug quedó registrado con evidencia en `pendientes/` y se implementó solo después de la aprobación.
