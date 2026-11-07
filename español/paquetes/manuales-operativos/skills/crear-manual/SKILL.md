---
name: crear-manual
description: Crea un manual MAN para un procedimiento operativo que no tiene ninguno, con requisitos, pasos con resultado esperado, verificación, reversión y problemas frecuentes.
resuelve: [procedimientos-sin-manual, pasos-no-ejecutables, procedimientos-sin-reversion]
---

# Crear manual

## Cuándo usarla

- Un procedimiento (desplegar, rotar una clave, restaurar una copia, responder a un incidente) no tiene manual.
- La persona pide documentar una operación.

## Pasos

1. Crea el manual: `python3 $P/scripts/comun/fichas.py nueva manual --slug desplegar-api --en despliegue --titulo "Desplegar la API"`. Nace `borrador`.
2. «Cuándo usarlo»: la situación concreta que lo dispara.
3. «Requisitos»: accesos y herramientas con versión; variables como `<NOMBRE>` y de dónde se obtienen.
4. «Pasos»: uno por línea con la forma `` `comando` → resultado esperado ``. Saca los comandos de los scripts del proyecto (CI, `Makefile`, `package.json`), no de memoria.
5. «Verificación»: cómo se comprueba que funcionó (URL de salud, consulta, métrica).
6. «Cómo revertir»: los pasos inversos, igual de exactos.
7. «Problemas frecuentes»: síntoma, causa y solución que ya se conozcan; si no hay, la tabla queda vacía.
8. Deja `ultima_verificacion: null`: la pone la persona al probarlo.

## Resultado

- Un manual `MAN-<fecha>-<slug>.md` en `borrador`, con todos los pasos ejecutables y su reversión.
