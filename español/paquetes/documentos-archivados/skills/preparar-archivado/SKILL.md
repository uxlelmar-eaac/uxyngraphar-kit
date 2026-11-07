---
name: preparar-archivado
description: Comprueba la ruta de un documento que la persona quiere retirar y le entrega el comando exacto de archivo.py archivar, que solo ella puede ejecutar.
resuelve: [documentos-retirados-sin-archivar, archivo-historico-alterado]
---

# Preparar archivado

## Cuándo usarla

- La persona quiere retirar un documento (un informe viejo, una especificación sustituida) sin perderlo.

## Pasos

1. Comprueba que la ruta existe y es un archivo. No puede estar bajo `uxyngraphar/paquetes/` (el script lo rechaza).
2. Entrega a la persona el comando, con la ruta desde la raíz de la app:
   `python3 $P/scripts/archivo.py archivar docs/especificacion-v1.md --humano`
3. Explica qué hará: copia el archivo a `uxyngraphar/trabajo/documentos-archivados/archivo/<fecha-de-hoy>/especificacion-v1.md`, sin borrar el original. Falla si ese mismo nombre ya se archivó hoy.
4. Si la persona quiere que algo del documento siga a mano, propón guardarlo antes como nota con `notas-de-memoria`.

## Resultado

- La persona tiene el comando exacto y sabe qué hará; el agente no ha escrito en `archivo/`.
