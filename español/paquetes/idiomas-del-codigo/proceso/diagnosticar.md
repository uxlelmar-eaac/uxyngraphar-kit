---
fase: diagnosticar
resuelve: [codigo-en-idioma-mezclado]
skills: [revisar-idioma, consultar-glosario]
---

# Fase: diagnosticar

## Objetivo

Saber, antes de escribir, en qué idioma está el código que vas a tocar, qué términos del dominio pueden quedarse sin traducir y qué problemas de idioma ya estaban.

## Entradas

- El pedido de la persona y los archivos o carpetas que afecta.
- El glosario `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md`, si existe.
- Los ajustes efectivos (`raices`, `extensiones`, `excluir`).

## Pasos

1. Aplica la skill `revisar-idioma` sobre los archivos que vas a modificar y anota los nombres de archivo no ASCII heredados.
2. Aplica la skill `consultar-glosario` para saber qué términos del dominio pueden quedarse sin traducir.
3. Mira el idioma del código que rodea al cambio (identificadores, logs, comentarios): si está en otro idioma, lo nuevo va en inglés igualmente y lo antiguo no se renombra de paso (`referencia/idioma.md`, «Código antiguo en otro idioma»).
4. Localiza los textos para el usuario que tocará el pedido y dónde están los archivos de locale del proyecto.

## Criterio de salida

- Tienes la lista de problemas de idioma heredados en los archivos afectados (puede estar vacía).
- Sabes qué términos del dominio están permitidos y cuáles traducir.
