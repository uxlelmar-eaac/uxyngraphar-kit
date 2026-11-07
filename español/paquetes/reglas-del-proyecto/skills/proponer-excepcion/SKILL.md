---
name: proponer-excepcion
description: Propone una excepción pendiente a una regla activa para unos archivos y un plazo, con el motivo, y deja esa parte del trabajo en espera hasta que una persona la apruebe.
resuelve: [reglas-incumplidas-en-silencio]
---

# Proponer excepción

## Cuándo usarla

- Una regla activa impide cumplir el pedido y no hay forma razonable de cumplir ambas cosas.
- Un archivo concreto necesita lo que la regla prohíbe (por ejemplo, el `console.log` del arranque en `src/main.ts`).

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva excepcion --slug <slug>`. Nace `pendiente` en `excepciones/`.
2. Rellena `regla` (id exacto `REG-…`), `archivos` (globs a los que se aplica; `[]` = todos los de la regla), `hasta` (`AAAA-MM-DD` o `null`) e `instruccion` si la hay.
3. En el cuerpo, el motivo: por qué no se puede cumplir la regla y qué alternativa se descartó.
4. Mientras esté `pendiente` no excusa nada: no entregues esa parte como terminada. Sigue con lo que no dependa de ella.
5. Di a la persona qué decide y con qué comando: `fichas.py estado EXC-… aprobada --humano` (y que escriba `aprobada_por`), o `rechazada`.

## Resultado

- Una ficha `EXC-…` en `pendiente` que cita una regla existente, con archivos acotados.
