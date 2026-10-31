---
id: EVO-20261030-ajustes-y-envio-sugerencias
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - PROTOCOLO.md
  - AGENTES.md
  - REGLAS.md
  - 46-evolucion-documentacion/_PROTOCOLO.md
  - 97-ajustes-locales/INDICE.md
  - 10-guias/ajustes-locales.md
  - 10-guias/envio-sugerencias.md
  - 10-guias/configuracion-uxyngraphar.md
  - 00-nucleo/frontmatter/evolucion.md
proposed_at: 2026-10-30
instruction_derivada: solicitud-humana-20261030-ajustes-envio
---
# EVO-20261030 — Ajustes locales y envío de sugerencias (R-25)

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita (2026-10-30).

## Qué faltaba

La 46 era un buzón que se quedaba en el proyecto: una mejora aprobada no podía usarse hasta que llegara al pack (editar el núcleo rompe la siguiente actualización), y para que llegara había que mandar a mano el informe de `exportar-evo.py`.

## Decisión humana

Regla **R-25** con dos vías, las dos decididas por una persona:

- **Aplicar en local** sin tocar el núcleo: ajustes en `97-ajustes-locales/` (contenido del proyecto), creados con `ajustes.py` desde una EVO aprobada, con huella del archivo que complementan para avisar tras cada actualización y retirarlos cuando la mejora llega al pack.
- **Enviar al pack**: `feedback.py`, opt-in explícito y apagado por defecto (es feedback con garantías de telemetría: consentimiento registrado, datos mínimos y limpios, nada automático, revocable con borrado remoto), y un servidor de referencia en el repo fuente (retirado antes de publicar 1.0.0 por EVO-20261030-colaboracion-al-instalar: el receptor oficial es el backend de uxyngraphar, NestJS + Postgres, repo uxyngraphar-backend).
