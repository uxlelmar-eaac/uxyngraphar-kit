---
id: EVO-20261015-control-construccion-universal
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/controlar.py
  - scripts/control/
  - 10-guias/elegir-pack.md
  - 10-guias/control-de-construccion.md
proposed_at: 2026-10-15
instruction_derivada: solicitud-humana-20261015-universal
---
# EVO-20261015 — uxyngraphar universal y control real de construcción

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita («asume las mejores decisiones… utilizarlo en cualquier aplicación con control real», 2026-10-15) en la versión **1.0.0**.

## Qué faltaba

Las reglas (límite de 350 líneas, instrucción previa, anclas, espejo) solo se verificaban por documentación o con avisos; nada las hacía cumplir sobre el código, la configuración por proyecto estaba en prosa y no había guía para elegir pack según el tipo de aplicación. Los archivos comunes de los dos packs se mantenían copiando a mano.

## Cambio aplicado

- `controlar.py` + `scripts/control/`: puerta con cinco controles y niveles configurables; enlazada en ganchos git, CI y `doctor.py`.
- `docs/uxyngraphar.config.json` (clase P) generado por detección de pila.
- Guías `elegir-pack` y `control-de-construccion`.
- `_compartido/` + `construir-packs.py` (solo repo uxyngraphar): una fuente para lo idéntico.

Sin cambios de plantillas ni de estructura de carpetas.
