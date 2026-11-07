---
fase: abrir-auditoria
resuelve: [investigaciones-sin-alcance, auditorias-abandonadas]
skills: [revisar-activas]
---

# Fase: abrir auditoría

## Objetivo

Empezar una investigación con alcance, preguntas y método escritos, sin superar el número de auditorías activas.

## Entradas

- La pregunta de la persona.
- Las auditorías existentes y los ajustes `max_activas` y `dias_sin_cambios`.

## Pasos

1. Aplica `revisar-activas`. Si ya hay una auditoría activa sobre lo mismo, continúa esa. Si hay `max_activas`, pregunta cuál cerrar o posponer antes de abrir otra.
2. Abre la ficha: `python3 $P/scripts/comun/fichas.py nueva auditoria --slug <slug> --titulo "…"`. Nace `activa` en `uxyngraphar/trabajo/auditorias-tecnicas/en-progreso/`. Si la persona la quiere para más adelante, pásala a `pendiente`.
3. Rellena «Alcance» (incluye y excluye: módulos, rutas, entornos) y `areas` del frontmatter.
4. Escribe «Preguntas»: de una a cinco, cada una con respuesta posible («¿qué consulta domina el tiempo del listado de pedidos?», no «¿está bien la base de datos?»).
5. Esboza «Método»: qué vas a mirar y con qué comandos o mediciones.

## Criterio de salida

- Ficha `AUD-…` `activa` con alcance, preguntas y método.
- El número de activas no supera `max_activas`.
