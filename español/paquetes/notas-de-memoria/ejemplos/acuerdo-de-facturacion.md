# Caso: un acuerdo de facturación que cambia

## Pedido 1

«Apunta que el cliente Acme ahora factura a 60 días, no a 30. Me lo confirmó hoy su contable.»

**guardar-nota.** No es una decisión técnica, ni una regla del código, ni un procedimiento: es memoria. El pedido corrige algo ya apuntado («ahora… no a 30»), así que pide expresamente tocar la nota anterior; **buscar-en-memoria** la localiza y no se abre nada más:

```
$ python3 $P/scripts/notas.py buscar acme
memoria/MEM-20260115-acme-facturacion.md:9: # Acme factura a 30 días
```

**registrar-nota** (skill):

```
python3 $P/scripts/comun/fichas.py nueva nota --slug acme-facturacion-60 --titulo "Acme factura a 60 días"
```

```yaml
fuente: "conversación con la persona 2026-11-06 (confirmado por la contabilidad de Acme)"
valida_hasta: null
```

«Por qué importa»: «los recordatorios de cobro no deben salir antes del día 60».

**archivar-nota-caducada** (skill): en `MEM-20260115-acme-facturacion` se añade «Sustituida por MEM-20261106-acme-facturacion-60 el 2026-11-06».

```
python3 $P/scripts/comun/fichas.py estado MEM-20260115-acme-facturacion archivada
python3 $P/scripts/comun/verificar.py
```

## Pedido 2 (otro día)

«Arregla el texto del recordatorio de cobro.» El pedido no menciona la memoria: **buscar-en-memoria** se salta. El agente no abre `memoria/` aunque sepa que hay notas sobre cobros; si el texto dependiera del plazo, preguntaría si quiere que busque en la memoria.

## Pedido 3

«Ya no usamos `docs/especificacion-cobros-v1.md`; guárdalo en el histórico.» Retirar un documento entero no es una nota: cae en «Fuera de alcance» y el agente propone `documentos-archivados`.

## Resultado

- Una nota vigente con fuente y la anterior archivada con la causa.
- Memoria no leída en un pedido que no la pedía.
- El archivado del documento, derivado a su paquete.
