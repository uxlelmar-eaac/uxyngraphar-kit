# 0005 · El mismo bloque completo en cada archivo de agente

- **Estado:** aceptada
- **Fecha:** 2026-11-10

## Contexto

Cada agente lee su propio archivo de instrucciones al empezar: Claude Code lee `CLAUDE.md`; Codex y otros, `AGENTS.md`; Copilot, `.github/copilot-instructions.md`. No se puede confiar en que un agente siga un puntero a otro archivo.

## Decisión

El motor escribe el mismo bloque completo, entre `<!-- uxyngraphar:inicio -->` y `<!-- uxyngraphar:fin -->`, en `AGENTES.md`, `AGENTS.md` y `CLAUDE.md` (los crea si faltan) y en `.github/copilot-instructions.md` si el proyecto ya lo tiene. El resto de cada archivo es de la persona y no se toca. Al retirar uxyngraphar se quita el bloque y el archivo solo se borra si queda vacío.

## Consecuencias

- Los tres archivos dicen lo mismo sobre uxyngraphar; lo propio del proyecto puede ser distinto en cada uno.
