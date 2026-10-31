---
id: EVO-20261029-memoria-del-sistema
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
  - 95-memoria/INDICE.md
  - 10-guias/memoria.md
  - 10-guias/organizacion-estados-fechas.md
  - 10-guias/configuracion-uxyngraphar.md
  - 10-guias/control-de-construccion.md
  - 10-guias/respaldos.md
  - 00-nucleo/eficiencia-ia.md
  - 35-herramientas/autorizadas/decisiones-pendientes.md
proposed_at: 2026-10-29
instruction_derivada: solicitud-humana-20261029-memoria
---
# EVO-20261029 — Memoria del sistema (R-24)

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita (2026-10-29) en la versión **1.0.0**.

## Qué faltaba

Las fichas que cumplían su ciclo terminaban en `06-listas-para-eliminar` y de ahí se borraban. Se perdía la historia del proyecto, y lo que quedaba en `04-archivadas` seguía creciendo dentro del alcance del agente.

## Decisión humana

Regla **R-24 — memoria del sistema: nada se borra.** Lo que antes se borraba pasa a `95-memoria/`, una carpeta que solo se añade, que solo consulta una persona (`scripts/memoria.py`) y que el agente no lee. Detalle en `10-guias/memoria.md`.

Opciones elegidas en el plan:

- Carpeta `95-memoria` (fuera de la numeración de trabajo, después de `90-archivo`).
- Pasar a la memoria lo propone `depurar` y lo confirma una persona; el modo automático queda para más adelante.
- `purgar` existe, solo para personas y para datos sensibles; un proyecto puede desactivarlo.
- El nombre del estado `06-listas-para-eliminar` no cambia en esta versión (cambiarlo sería incompatible).

## Ajustes al aplicarla

- Integridad por huella sha256 en `catalogo.jsonl`; el control `memoria` de `controlar.py` (bloqueante) y el CI rechazan cualquier cambio hecho a mano.
- Barreras para el agente: reglas `deny`, `.cursorignore`/`.geminiignore`/`.aiexclude`, `CODEOWNERS`, línea en `AGENTES.md` y herramientas del pack que la ignoran.
- Una ficha que todavía enlaza un documento vivo no se guarda: se pide quitar el enlace o cambiarlo por `memoria:ID`.
- En un plan de `depurar`, `"accion": "eliminar"` es sinónimo de `memoria`: también va a la memoria.

## Verificación

`construir-packs.py --verificar`, validadores, suites de ambos packs y prueba de actualización en verde.
