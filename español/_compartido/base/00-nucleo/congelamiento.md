# Congelamiento del núcleo

## Qué está congelado

El **núcleo** (clase **N**) son las reglas del juego: `AGENTES.md`, `REGLAS.md`, `PROTOCOLO.md`, `00-nucleo/` (menos las plantillas P), `10-guias/`, `55-automatizaciones/`, `scripts/`, `_PLANTILLA*`, `_PROTOCOLO*` y `VERSION.md`. Ningún agente los modifica en un proyecto alineado. La clasificación completa por archivo vive en `scripts/nucleo/clasificacion.py` (fuente única):

| Clase | Qué es | Ejemplos | Al actualizar |
|-------|--------|----------|---------------|
| **N** núcleo | Reglas, guías, scripts, plantillas de ficha | `REGLAS.md`, `10-guias/*`, `_PLANTILLA.md` | Se reemplaza si el proyecto no lo editó |
| **P** plantilla a rellenar | Se completa en cada proyecto | `00-nucleo/configuracion-proyecto.md`, `ESTADO.md` | Nunca se sobrescribe; se avisa si la plantilla cambió |
| **M** mixto | Índices con filas del proyecto | `*/INDICE.md`, `README.md` | Nunca se sobrescribe |
| **C** contenido | Fichas, instrucciones, rutas, espejo, ADR | `25-areas/*`, `05-instrucciones/**/*.md` | Jamás se toca |

## Cómo se hace cumplir

1. **Huellas:** `docs/.uxyngraphar.lock` guarda el hash de cada archivo tal como lo entregó el pack. `python3 docs/scripts/verificar-nucleo.py` falla si un archivo N cambió (`NUCLEO-MODIFICADO`), se borró (`NUCLEO-ELIMINADO`), si aparece uno nuevo en zona reservada (`NUCLEO-EXTENDIDO`) o hay archivos fuera de la taxonomía (`FUERA-DE-TAXONOMIA`).
2. **Permisos:** `instalar-pack.py --proteger` genera reglas `deny` de edición para agentes (`.claude/settings.json`) y un bloque `CODEOWNERS` para exigir revisión humana.
3. **Gancho y CI:** `instalar-ganchos.py` ejecuta la verificación en `pre-commit`; el CI la repite (ver [ci-validacion-documentacion.md](../10-guias/ci-validacion-documentacion.md)).

## Qué sí fluye

El **contenido** del proyecto (clase C) se actualiza con cada instrucción aprobada. Congelado = las reglas, no el contenido.

## Cómo proponer mejoras al núcleo

1. Abrir ficha en `46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` del proyecto (`decisiones.py new evo --slug …`). Es el **único canal**: la 46 de un proyecto es un buzón de propuestas hacia el pack fuente (uxyngraphar), no una cola de trabajo local.
2. El humano decide: aprueba, pospone o rechaza.
3. Si aprueba, el cambio se implementa **en el pack fuente**, se publica una versión nueva y el proyecto la recibe con `actualizar-pack.py` ([actualizar-nucleo.md](../10-guias/actualizar-nucleo.md)).
4. **Sin excepciones locales (R-20):** no existe forma de «aceptar» una edición del núcleo en el proyecto. Si está alterado, el humano lo restaura con `actualizar-pack.py --apply --restaurar-nucleo` (el respaldo conserva la copia alterada).

## Reglas concisas (R-20)

1. El núcleo solo cambia en uxyngraphar y entra con `actualizar-pack.py`.
2. Nadie del proyecto edita, borra, renombra ni amplía zonas N, ni toca `.uxyngraphar.lock`, `.claude/settings.json`, `CODEOWNERS`, CI o ganchos.
3. Mejoras → solo ficha EVO en 46.
4. No se evita la verificación (`--no-verify`, `--warn`).
5. Núcleo alterado → parar, avisar, restaurar (humano). Diagnóstico completo: `python3 docs/scripts/doctor.py --pack RUTA_PACK`.

## Límites honestos

Las reglas `deny` frenan las herramientas de edición de los agentes, pero un agente con shell podría saltárselas; por eso hay capas independientes: gancho `pre-commit`, CI con `verificar-nucleo.py --contra <pack>` (no depende del lock), `CODEOWNERS` con revisión obligatoria y el sello del lock.
