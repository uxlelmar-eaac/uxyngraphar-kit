---
name: consultar-glosario
description: Lista los términos del dominio que el proyecto permite sin traducir y explica cómo proponer uno nuevo a la persona sin editar el glosario.
resuelve: [codigo-en-idioma-mezclado]
---

# Consultar glosario

## Cuándo usarla

- En `diagnosticar`, antes de escribir código con conceptos de negocio.
- Cuando un término del pedido (por ejemplo `expediente`, `retencion_fiscal`) no tiene traducción precisa al inglés.
- Al reflejar un campo de un contrato externo (facturación electrónica, pasarela de pago) en un DTO o adaptador.

## Pasos

1. Ejecuta `python3 $P/scripts/glosario.py terminos`. Imprime la primera columna de `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md`, o «(glosario vacío o inexistente: todo término va en inglés)».
2. Un término de la lista se usa en ASCII, con el casing del código y sin conjugar ni pluralizar en su idioma (`expedienteIds`, no `expedientes`).
3. Un campo de contrato externo se refleja tal cual solo en la frontera (DTO, esquema, adaptador); pasado el adaptador, el dominio usa nombres en inglés con un mapeo explícito.
4. Si el término no está y crees que debería: no lo añadas. Propón a la persona la fila (término, glosa en inglés, definición, tipo, fuente) y, mientras tanto, tradúcelo.
5. Si el glosario no existe y la persona quiere empezarlo: `python3 $P/scripts/glosario.py iniciar` crea la plantilla vacía; la rellena ella.

## Resultado

- Sabes qué términos puedes dejar sin traducir; los demás van en inglés.
