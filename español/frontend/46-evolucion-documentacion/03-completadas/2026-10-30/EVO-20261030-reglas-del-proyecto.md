---
id: EVO-20261030-reglas-del-proyecto
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - 96-reglas-proyecto/_PROTOCOLO.md
  - 96-reglas-proyecto/_PLANTILLA-regla.md
  - 96-reglas-proyecto/_PLANTILLA-excepcion.md
  - 96-reglas-proyecto/INDICE.md
  - AGENTES.md
  - 05-instrucciones/_PLANTILLA-compacta.md
  - 10-guias/configuracion-uxyngraphar.md
  - 10-guias/control-de-construccion.md
  - scripts/reglas/reglas_proyecto.py
  - scripts/control/reglas_control.py
proposed_at: 2026-10-30
instruction_derivada: solicitud-humana-20261030-reglas-proyecto
---
# EVO-20261030 — Reglas del proyecto (96-reglas-proyecto)

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita del mantenedor (uxlelmar, 2026-10-30).

## Qué faltaba

El equipo no tenía dónde escribir las reglas de **su** código (convenciones, prohibiciones) para que el agente las cumpla de forma estricta y verificable, sin tocar las reglas del núcleo.

## Decisión humana

1. Viven en su propia carpeta con sus propias plantillas; el núcleo solo le dice al agente dónde mirar.
2. Ninguna regla inicial (pensado para el usuario final); las reglas del núcleo no se alteran.
3. Excepciones con la mejor opción por defecto (declarada en la instrucción, aprobada al aprobarla) y configurables en `uxyngraphar.config.json`.
4. Estricto y económico en tokens.
5. El agente puede crear, editar, mejorar o eliminar reglas, pero solo con aprobación humana explícita.

## Resultado

Publicado en **1.0.0** (CHANGELOG). Pruebas: `scripts/reglas/test_reglas.py`.
