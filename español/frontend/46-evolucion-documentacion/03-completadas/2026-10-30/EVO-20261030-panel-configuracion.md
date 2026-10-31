---
id: EVO-20261030-panel-configuracion
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - 10-guias/configuracion-uxyngraphar.md
proposed_at: 2026-10-30
instruction_derivada: solicitud-humana-20261030-panel-configuracion
---
# EVO-20261030 — Panel de configuración visual e instalador visual

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita del mantenedor (uxlelmar, 2026-10-30).

## Qué faltaba

La configuración de cada proyecto (`uxyngraphar.config.json`) solo se veía en texto (`uxyngraphar configuracion`) y se editaba a mano. No había forma de ver todos los proyectos de un equipo ni de fijar preferencias una vez para todos. El instalador de una línea terminaba en la terminal y decidía el PATH sin preguntar.

## Decisión humana

- El configurador es **visual**: abre una pantalla en el navegador local y desde ahí se configura cada proyecto y el sistema.
- La configuración del sistema es una **plantilla para proyectos nuevos**: se aplica al instalar y, si la persona lo pide y tras ver los cambios, a proyectos existentes. Cada proyecto sigue mandando con su archivo en git (el CI y el equipo ven lo mismo).
- El **instalador** también es visual: se instala con el comando de una línea y al terminar se abre la interfaz con todo lo que pasó en la terminal y las decisiones iniciales.
- Sin cambios en las reglas del núcleo (R-xx). El panel no cambia nada si lo ejecuta CI o un agente.

## Resultado

Publicado en **1.0.0** (CHANGELOG). Pruebas: `instalador/test_panel.py`, `instalador/test_arranque.py`, `instalador/test_web.py`.
