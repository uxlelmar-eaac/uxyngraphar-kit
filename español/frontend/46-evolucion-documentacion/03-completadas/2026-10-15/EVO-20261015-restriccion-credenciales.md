---
id: EVO-20261015-restriccion-credenciales
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/control/secretos.py
  - scripts/escanear-secretos.py
  - scripts/nucleo/proteccion.py
  - REGLAS.md
proposed_at: 2026-10-15
instruction_derivada: solicitud-humana-20261015-credenciales
---
# EVO-20261015 — Restricciones para que no se filtren credenciales

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita («verifica que no se vayan credenciales o claves, coloca restricciones», 2026-10-15) en la versión **1.0.0**.

## Qué faltaba

R-12 prohibía credenciales en documentación, pero la puerta de control solo miraba código (omitía `docs/` y `.md`), no bloqueaba archivos `.env`/llaves, no había auditoría del historial y los agentes podían leer archivos de credenciales.

## Cambio aplicado

- Detección ampliada y enmascarada en `controlar.py`; bloqueo por nombre de archivo.
- `escanear-secretos.py` (árbol e historial).
- Reglas `deny` de lectura/escritura para agentes; patrones en `.gitignore`; chequeo `secretos` en `doctor.py`.

Sin cambios de plantillas ni de estructura de carpetas.
