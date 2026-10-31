---
id: EVO-20261028-politica-idioma
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
  - 00-nucleo/politica-idioma.md
  - 00-nucleo/glosario-dominio.md
  - 00-nucleo/agentes-detalle.md
  - 05-instrucciones/_PROTOCOLO.md
  - 05-instrucciones/_PLANTILLA.md
  - 05-instrucciones/_PLANTILLA-compacta.md
  - 10-guias/control-de-construccion.md
  - scripts/control/idioma.py
  - scripts/control/uxyngraphar_config.py
  - scripts/control/puerta.py
  - scripts/controlar.py
  - scripts/ganchos/instalar_ganchos.py
proposed_at: 2026-10-28
instruction_derivada: solicitud-humana-20261028-idioma
---
# EVO-20261028 — Política de idioma del código del producto (R-22)

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita (2026-10-28) en la versión **1.0.0**.

## Qué faltaba

El código se escribía en el idioma del humano que pedía el requerimiento y se mezclaban idiomas en identificadores (`obtenerUserById`). No había regla, configuración ni control que lo impidiera.

## Decisiones humanas

1. La política aplica **solo al código del producto**; `docs/` sigue en el idioma del pack.
2. Los parámetros viven en `uxyngraphar.config.json` (sección `idioma`), sin archivo de override aparte.
3. Legacy flexible: renombrar solo si todos los usos están en `anclas_codigo`; si no, ficha en 45; contratos públicos con ADR + migración.
4. Glosario de dominio como plantilla del proyecto (clase P), enlazado con el registro de ids compartidos.

## Ajustes sobre el borrador original

- El formato de nombres lo decide la guía de cada pila; la política decide el idioma (el borrador imponía camelCase a Python/Go/Dart).
- Pluralización de términos de dominio sin contradicción: sufijo de colección en inglés, salvo plural registrado como término propio.
- Contratos externos (CFDI/SAT, terceros) reflejados tal cual en la frontera y registrados en el glosario.
- Exenciones explícitas: código generado, vendorizado, migraciones aplicadas, datos de prueba.
- Archivos de locale fuera del cómputo de código (R-19, R-21); i18n distinto en cliente (labels) y servidor (códigos de error estables, plantillas de correo).
- Autochequeo con casilla en la instrucción (trazable) en lugar de «verificar en silencio».
- Controles en **aviso** por defecto para adopción gradual; lo heurístico nunca bloquea.

## Verificación

`test_idioma.py` (heurística, glosario, legacy, locales, `docs/` excluido, commits, ramas, CI) y suites completas de ambos packs en verde.
