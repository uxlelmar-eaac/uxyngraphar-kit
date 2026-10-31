---
id: EVO-20261015-ahorro-tokens-herramientas
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - AGENTES.md
  - 05-instrucciones/_PLANTILLA-compacta.md
  - scripts/contexto.py
  - scripts/presupuesto.py
  - scripts/espejo-mapa.py
  - scripts/decisiones/decisiones.py
proposed_at: 2026-10-15
instruction_derivada: solicitud-humana-20261015-tokens
---
# EVO-20261015 — Ahorro de tokens y herramientas de contexto

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita («todo aprobado», 2026-10-15) en la versión **1.0.0**.

## Qué faltaba

El arranque de un agente costaba ~5 000 tokens (AGENTES + eficiencia-ia + ciclo-vinculante), cada instrucción nueva partía de una plantilla de ~170 líneas con campos casi siempre vacíos y el agente abría uno a uno los documentos y archivos de código sin un límite en tokens.

## Cambio aplicado

- `AGENTES.md` compacto (~540 tokens); el detalle pasa a `00-nucleo/agentes-detalle.md` (bajo demanda).
- `_PLANTILLA-compacta.md` (`decisiones.py new instruccion --plantilla compacta`).
- `contexto.py`: paquete de lectura de una instrucción (ficha compacta, `lectura_minima` con `#sección`, `espejo_leer`, código por rango) con presupuesto y lista de omitidos.
- `presupuesto.py`: medidor de arranque / instrucción / documentos más pesados.
- `decisiones.py cerrar` y `estado` (ESTADO.md autogenerado); `espejo-mapa.py` (mapa compacto y código sin espejo).
- `empaquetar-pack.py` (.zip con manifiesto), `instalar-pack.py --analizar --claude-md`, `flota.py`.

## Verificación

`presupuesto.py arranque` ≤ 1 500 tokens (verificado en pruebas); 160+ pruebas en cada pack.
