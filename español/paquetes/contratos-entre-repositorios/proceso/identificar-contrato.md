---
fase: identificar-contrato
resuelve: [ids-compartidos-inconsistentes]
skills: []
---

# Fase: identificar-contrato

## Objetivo

Saber qué contrato toca el pedido, qué rol tiene este repositorio y si el contrato ya existe aquí o en el repositorio hermano.

## Entradas

- El pedido: qué ruta se consume, publica o cambia.
- Los contratos de `uxyngraphar/trabajo/contratos-entre-repositorios/` y su `REGISTRO.md`.

## Pasos

1. Lista los contratos: `python3 $P/scripts/comun/fichas.py listar contrato` y lee `REGISTRO.md` si existe.
2. Determina el rol de este repositorio: `proveedor`, `consumidor` o `bff` (ver `COMPONENTES.md`).
3. Busca el `id_compartido` de la ruta. Si este repositorio no lo tiene y el hermano sí (consulta su `REGISTRO.md` solo si `otros_repos` lo apunta o el pedido lo pide), reutiliza **el mismo** id.
4. Si el cambio es incompatible para los consumidores (quita o renombra campos, cambia la ruta o el método), anótalo: `registrar-contrato` aplicará la skill `versionar-contrato`.
5. Si es un cambio del consumidor, lee `$P/referencia/sincronizar.md`.

## Criterio de salida

- Sabes el `id_compartido` (existente o nuevo), el rol de este repositorio y si el cambio es incompatible.
