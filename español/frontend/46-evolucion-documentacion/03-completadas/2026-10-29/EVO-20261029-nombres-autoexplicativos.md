---
id: EVO-20261029-nombres-autoexplicativos
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - PROTOCOLO.md
  - REGLAS.md
  - AGENTES.md
  - 00-nucleo/nombres-autoexplicativos.md
  - 00-nucleo/agentes-detalle.md
  - 00-nucleo/INDICE.md
  - 05-instrucciones/_PROTOCOLO.md
  - 05-instrucciones/_PLANTILLA.md
  - 05-instrucciones/_PLANTILLA-compacta.md
  - 10-guias/sync-documentacion-pr.md
  - 10-guias/tarjeta-referencia-humana.md
proposed_at: 2026-10-29
instruction_derivada: solicitud-humana-20261029-nombres
---
# EVO-20261029 — Nombres autoexplicativos (R-23)

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita (2026-10-29) en la versión **1.0.0**.

## Qué faltaba

R-22 fija el idioma de los identificadores, pero no su calidad: nada pedía que un nombre se entendiera sin comentario ni distinguía comentarios del *qué* (señal de renombrar) de comentarios del *porqué* (reglas de negocio).

## Decisión humana

Regla **R-23 — nombres autoexplicativos**: el nombre es la documentación primaria y el comentario la excepción. Contenido completo (principio, ocho reglas, excepciones, cumplimiento) en `00-nucleo/nombres-autoexplicativos.md`.

## Ajustes al aplicarla

- Ejemplos de código en inglés (R-22); el vocabulario del dominio se enlaza con el glosario de dominio.
- Cumplimiento por casilla de autochequeo en la instrucción, ítem de code review en la checklist de PR y en la tarjeta humana, y linters del lenguaje configurados por el proyecto.
- Sin control nuevo en `controlar.py`: la calidad de un nombre no es verificable de forma fiable por heurística, y la regla del repo fuente impide añadir controles bloqueantes.
- Legacy: renombrar solo dentro de `anclas_codigo`; si no, ficha en 45 (como R-22).

## Verificación

`construir-packs.py --verificar`, validadores y suites de ambos packs en verde.
