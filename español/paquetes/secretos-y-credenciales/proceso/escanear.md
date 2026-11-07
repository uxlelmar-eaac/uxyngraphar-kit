---
fase: escanear
resuelve: [secretos-en-el-codigo, archivos-de-secretos-versionados, escaneo-silenciado]
skills: [escanear-secretos, sustituir-por-variable-de-entorno]
---

# Fase: escanear

## Objetivo

Demostrar, antes de cerrar o de proponer un commit, que el cambio no introduce secretos ni archivos de secretos, sin haber debilitado el escáner.

## Entradas

- Las rutas tocadas y la lista de hallazgos previos de `diagnosticar`.

## Pasos

1. Aplica la skill `escanear-secretos` sobre lo tocado; si vas a proponer un commit, también con `--git`.
2. Compara con `diagnosticar`: todo hallazgo nuevo es tuyo y se corrige ahora con `sustituir-por-variable-de-entorno` (o se renombra el archivo a plantilla, `.env` → `.env.example`, sin valores).
3. Revisa tu propio diff: no puede añadir entradas a `excluir` o `permitir` en `ajustes.json` ni marcas `uxyngraphar:permitir-secreto` sin permiso explícito de la persona.
4. Un hallazgo que parezca un secreto real (tuyo o heredado) pasa a `atender-incidente`.
5. Ejecuta las verificaciones del paquete: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/secretos.py`.

## Criterio de salida

- `secretos.py` sale con código 0 sobre lo que tocaste; los hallazgos heredados están comunicados a la persona.
- Tu cambio no amplía `excluir`, `permitir` ni añade marcas sin permiso.
