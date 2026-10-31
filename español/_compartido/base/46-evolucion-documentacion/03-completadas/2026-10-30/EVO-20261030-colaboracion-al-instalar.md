---
id: EVO-20261030-colaboracion-al-instalar
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - 10-guias/envio-sugerencias.md
  - 10-guias/configuracion-uxyngraphar.md
  - 10-guias/ajustes-locales.md
  - 46-evolucion-documentacion/_PROTOCOLO.md
  - scripts/feedback/cliente.py
  - scripts/feedback.py
  - scripts/control/uxyngraphar_config.py
proposed_at: 2026-10-30
instruction_derivada: solicitud-humana-20261030-colaboracion
---
# EVO-20261030 — Colaboración libre al instalar y receptor oficial

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita del mantenedor (uxlelmar, 2026-10-30).

## Qué faltaba

El envío de sugerencias existía pero nadie lo descubría: había que conocer `feedback.py activar`. Además enviaba también los ajustes locales (que el mantenedor no quiere recoger) y el receptor era un servidor de ejemplo en Python que no encajaba con la plataforma del proyecto (NestJS + Postgres).

## Decisión humana

- uxyngraphar es abierto y la colaboración debe ser **libre**: al instalar aparece «¿Te gustaría colaborar en la mejora de uxyngraphar?» con Sí y No, sin opción marcada, mostrando antes qué sale y qué no. Con Sí se recibe el feedback; con No no se recibe nada. Se pregunta una vez también al actualizar proyectos que aún no respondieron.
- Tras el Sí el envío es **automático solo cuando una persona usa uxyngraphar** (instalar y actualizar), con las fichas EVO nuevas o cambiadas. Nunca desde CI, ganchos ni el agente.
- Solo se recogen **fichas EVO** (mejoras integrales de la metodología): ni ajustes locales ni métricas de uso.
- El receptor oficial es el backend de uxyngraphar (`uxyngraphar-backend`); se elimina `servidor-sugerencias/` del repo fuente. La dirección vive en una sola constante (`URL_FEEDBACK_OFICIAL`), provisional hasta tener el dominio.

## Resultado

Publicado en **1.0.0** (CHANGELOG). Pruebas: `scripts/feedback/test_feedback.py`, `instalador/test_web.py`, `instalador/test_actualizar_web.py`.
