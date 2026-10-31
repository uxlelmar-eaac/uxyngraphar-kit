# Qué es uxyngraphar

**uxyngraphar** («contrato escrito firmado y sellado por todas las partes») es un **sistema documental de gobernanza humano–IA**.

- El **contrato** ata a la IA: solo trabaja con instrucciones que una persona aprobó.
- El **espejo** (`50-sistema-integral/`) mantiene la documentación alineada con el código.

## Qué entrega el kit

1. **Herramienta CLI** `uxyngraphar` (panel local, instalar, actualizar, estado…).
2. **Dos packs** autosuficientes (servidor / cliente) que se copian a `docs/` del proyecto.
3. **Protecciones** opcionales: reglas deny para agentes, CODEOWNERS, ganchos, CI.

## Qué no es

- No es un IDE.
- No sustituye git ni CI.
- No publica solo tu código: el pack vive **dentro** de tu repo en `docs/`.

## Dónde vive cada cosa

| Pieza | Ubicación |
|-------|-----------|
| Código del kit / packs | repo `uxyngraphar` → carpeta `español/` |
| Este manual | `documentacion/` (no se instala en proyectos) |
| Pack en tu app | `tu-repo/docs/` + `AGENTES.md` al lado |
