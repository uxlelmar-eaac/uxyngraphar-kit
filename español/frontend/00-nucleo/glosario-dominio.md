# Glosario de dominio (R-22)

> Plantilla del proyecto (clase **P**): la completa el equipo y las actualizaciones del pack no la sobrescriben. Las herramientas leen la **primera columna** como lista de términos permitidos en el código ([politica-idioma.md](politica-idioma.md) §3–§4).

Reglas para registrar un término:

- Solo términos **sin equivalente preciso en inglés**, nombres propios o campos de **contratos externos**.
- Primera columna en **ASCII** y con el casing del código (`retencion_fiscal`, `expediente`, `RegimenFiscal`).
- Sustantivo opaco: no se conjuga ni se pluraliza en su idioma (colecciones: `expedienteList`, `expediente_ids`).
- Debe estar presente en ambos repos (servidor y cliente) con la misma escritura si viaja en un contrato de API ([registro-ids-compartidos.md](registro-ids-compartidos.md)).

| Término | Glosa (en) | Definición | Tipo | Fuente | Responsable |
|---------|------------|------------|------|--------|-------------|
| `ejemplo_termino` | example term | Fila de ejemplo: reemplázala o bórrala. | dominio | — | `<equipo>` |

Tipos: `dominio` (concepto de negocio local) · `nombre-propio` (razón social, marca, producto) · `contrato-externo` (campo de un estándar o API de terceros, p. ej. CFDI/SAT; indicar versión o URL en **Fuente**).
