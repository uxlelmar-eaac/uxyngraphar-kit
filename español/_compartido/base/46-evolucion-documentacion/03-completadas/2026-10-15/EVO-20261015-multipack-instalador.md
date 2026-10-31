---
id: EVO-20261015-multipack-instalador
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/nucleo/clasificacion.py
  - scripts/nucleo/proteccion.py
  - scripts/ganchos/instalar_ganchos.py
  - 10-guias/elegir-pack.md
proposed_at: 2026-10-15
instruction_derivada: solicitud-humana-20261015-multipack
---
# EVO-20261015 — Varios packs por repositorio y asistente de instalación

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita («¿consideraste que quizá solo quiero backend, frontend o ambos, en distinto repo o en el mismo?», 2026-10-15) en la versión **1.0.0**.

## Qué faltaba

Instalar los dos packs en un mismo repositorio fallaba: ambos escribían `AGENTES.md` en la raíz, el bloque de `CODEOWNERS` del segundo reemplazaba al del primero y el gancho solo vigilaba un pack. El asistente no ofrecía instalar solo uno, ambos ni elegir dónde.

## Cambio aplicado

- `AGENTES.md`/`AGENTS.md`/`CLAUDE.md` se instalan junto a `docs/`; lock, configuración, `CODEOWNERS` y ganchos son por pack.
- Asistente con los escenarios servidor, cliente o ambos (mismo repo o repos distintos).

Sin cambios de plantillas ni de estructura de carpetas del pack.
