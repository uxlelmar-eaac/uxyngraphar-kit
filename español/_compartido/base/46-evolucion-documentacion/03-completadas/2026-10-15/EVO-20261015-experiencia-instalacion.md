---
id: EVO-20261015-experiencia-instalacion
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/nucleo/flujo.py
  - scripts/instalar-pack.py
  - scripts/actualizar-pack.py
  - scripts/doctor.py
proposed_at: 2026-10-15
instruction_derivada: solicitud-humana-20261015-ux-instalacion
---
# EVO-20261015 — Experiencia de instalación comprensible

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita («tu interfaz y tu procedimiento de los ejecutables es mal, no se entiende qué va a hacer, qué está haciendo, qué pasa si elijo X», 2026-10-15) en la versión **1.0.0**.

## Qué faltaba

El asistente y los scripts mostraban comandos y salidas técnicas sin explicar qué hacían, qué ocurría al elegir cada opción ni qué hacer después.

## Cambio aplicado

- Asistente visual con plan previo, explicación de cada opción, avance y resultado.
- Capa `flujo.py` con mensajes en lenguaje llano compartida por asistente y scripts.
- Salidas de `instalar-pack`, `actualizar-pack` y `doctor` con contexto y siguiente paso.

Sin cambios de plantillas ni de estructura de carpetas del pack.
