---
id: EVO-20261015-auditoria-instalacion-servidor
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: auditoria-proyecto-real
areas: []
propuesta_cambio:
  - scripts/nucleo/ci.py
  - scripts/nucleo/instalar.py
  - scripts/nucleo/lock.py
  - scripts/nucleo/proteccion.py
  - scripts/nucleo/doctor.py
  - scripts/control/puerta.py
  - scripts/nucleo/test_servidor.py
  - scripts/nucleo/flujo.py
  - scripts/actualizar-pack.py
proposed_at: 2026-10-15
instruction_derivada: solicitud-humana-20261015-ajuste-auditoria
---
# EVO-20261015 — Huecos del protocolo detectados al auditar un proyecto real

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita («analiza esta información y ajusta lo que corresponda del protocolo uxyngraphar», 2026-10-15) en la versión **1.0.0**.

## Qué faltaba

Una auditoría de un proyecto con uxyngraphar instalado (doctor sin errores) encontró que el protocolo se podía saltar o se degradaba sin que ninguna herramienta lo dijera:

1. Nada lo hacía cumplir en el servidor, y los workflows existentes estaban en subcarpetas que GitHub no lee.
2. `uxyngraphar.config.json` (niveles, exenciones, secretos permitidos) no estaba protegido.
3. El proyecto acababa versionando `*.pyc` y viendo cientos de archivos modificados solo por fin de línea.
4. El lock guardaba la ruta local de quien instaló.
5. 10 de 195 pruebas fallaban al ejecutarse desde un proyecto instalado.

## Cambio aplicado

Workflow de CI generado y diagnosticado por el doctor; configuración protegida; `.gitignore`/`.gitattributes` del pack; `fuente` del lock sin rutas locales; pruebas dependientes del repo fuente omitidas con motivo. Además, herramienta de doble clic (`Actualizar-uxyngraphar`) y revisión de protecciones tras actualizar, para que los proyectos ya instalados reciban estos cambios sin comandos. Detalle en el CHANGELOG 1.0.0.

## Fuera de alcance (queda como propuesta)

- **Comprobar R-02 con herramienta** (endpoint sin ficha en `15-rutas/`): hoy lo detecta solo una revisión manual; requiere extraer endpoints por pila (NestJS, Express, FastAPI…).
- **Exigir propietario real en `CODEOWNERS`** en CI (hoy es solo aviso del doctor).
- Los hallazgos propios del proyecto auditado (cookies, `trust proxy`, `.env.example`, Docker, refresh token…) no son del pack: se tratan en su repositorio.
