---
name: crear-sistema
description: Crea un sistema de gobernanza nuevo en el catálogo del kit con el generador (diseñar, generar, completar, probar y cerrar) hasta que valida y sus pruebas pasan.
---

# Crear un sistema

Skill para quien crea sistemas en el repositorio del kit (personas y agentes). El proceso completo, con sus límites y
cuándo preguntar, está en [`GUIA-PARA-AGENTES.md`](../../GUIA-PARA-AGENTES.md); el formato de la especificación, en
[`GENERADOR.md`](../../GENERADOR.md). Aquí está la secuencia de comandos. `$U` es `python3 motor/uxyngraphar.py` desde `español/`.

## Cuándo usarla

- La persona pide un sistema nuevo para un conjunto acotado de problemas que ningún sistema del catálogo cubre.
- No sirve para cambiar un sistema existente ni para instalar sistemas en un proyecto.

## Pasos

1. Catálogo actual y parecidos: `$U validar --json`; lee el `SISTEMA.md` de los que se parezcan. Si solapa, detente y pregunta.
2. Especificación de partida: `$U generar plantilla --id <id> --familia <familia>` (a un archivo) y rellénala, incluidas `memorias` (qué recordar y qué no del proyecto: va a `MEMORIAS.md`), `limites` (va a `LIMITES.md`) y `permisos` (acciones solo de la persona y rutas que la IA no toca: van al manifiesto y a `PERMISOS.md`), todo núcleo obligatorio.
3. Comprobar sin crear: `$U generar desde <spec.json> --json` hasta que `errores` esté vacío.
4. Crear: `$U generar desde <spec.json> --aplicar --json` (`aplicado: true`). Sin especificación: `$U crear <id> --titulo "…" --familia <familia> --json`.
5. Completar: `$U generar pendientes <id> --json` y haz lo que diga `siguiente` hasta `listo: true`; tras tocar `sistema.json`, `$U indice-sistema <id>`.
6. Probar: `$U validar <id> --json` sin errores; `$U sincronizar-comun` y las pruebas del sistema.
7. Cerrar: `CHANGELOG.md` con la versión del manifiesto y un resumen para la persona (qué cubre, qué deja fuera, cómo instalarlo con `$U instalar <id> --repo …`).

## Resultado

- `sistemas-de-gobernanza/<id>/` valida, sus pruebas pasan y `generar pendientes` dice `listo: true`.
