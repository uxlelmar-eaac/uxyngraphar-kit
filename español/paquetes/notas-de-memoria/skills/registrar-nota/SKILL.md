---
name: registrar-nota
description: Crea una nota MEM breve en memoria/ con lo que la persona quiere conservar, su fuente y hasta cuándo vale, sin secretos ni datos personales.
resuelve: [conocimiento-del-proyecto-perdido, notas-caducadas-tratadas-como-vigentes]
---

# Registrar nota

## Cuándo usarla

- La persona pide recordar algo que no es una decisión, una regla, un procedimiento ni deuda.

## Pasos

1. Crea la nota: `python3 $P/scripts/comun/fichas.py nueva nota --slug cliente-acme-facturacion --titulo "Acme factura a mes vencido"`. Nace `vigente` en `memoria/`.
2. Frontmatter:
   - `fuente`: de dónde sale («conversación con la persona 2026-11-06», «incidente del 2026-10-12»).
   - `valida_hasta`: fecha o condición («2027-03-31», «hasta que migre a la API v2»); `null` solo si no caduca.
3. «Qué hay que recordar»: una a tres frases.
4. «Por qué importa»: qué sale mal si se olvida.
5. Nada de claves, tokens, correos personales ni datos de clientes identificables.

## Resultado

- Una nota `MEM-<fecha>-<slug>.md` en `uxyngraphar/trabajo/notas-de-memoria/memoria/`, breve, fechada y con fuente.
