---
fase: archivar-documento
resuelve: [documentos-retirados-sin-archivar, archivo-historico-alterado]
skills: [preparar-archivado]
---

# Fase: archivar-documento

## Objetivo

Que un documento que se retira quede como copia fechada en el archivo, hecha por la persona, sin que el agente lea ni toque el archivo.

## Entradas

- La ruta del documento a archivar.

## Pasos

1. Aplica la skill `preparar-archivado`: comprueba la ruta y entrega a la persona el comando.
2. No ejecutes `archivo.py archivar` ni copies tú el archivo a `archivo/`: es una acción de la persona (límite 3).
3. No toques nada que ya esté en `archivo/`, ni siquiera para corregirlo.
4. Si la persona quiere además borrar o mover el original, hazlo solo cuando confirme que la copia existe. Si prefiere dejar una referencia en su lugar, sustituye el contenido por `$P/plantillas/aviso-de-retirada.md` rellenada.
5. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- La persona tiene el comando exacto para archivar (o confirma que ya lo ejecutó).
- Nada en `archivo/` ha sido leído ni editado por el agente.
