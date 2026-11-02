# Congelamiento del núcleo

## Qué está congelado

El **núcleo** (clase **N**) son las reglas del juego: `AGENTES.md`, `REGLAS.md`, `PROTOCOLO.md`, `00-nucleo/` (menos las plantillas P), `10-guias/`, `55-automatizaciones/`, `scripts/`, `_PLANTILLA*`, `_PROTOCOLO*` y `VERSION.md`. En un proyecto sembrado es un **framework de gobernanza**: nadie del proyecto (agente ni persona) lo altera. La clasificación completa por archivo vive en `scripts/nucleo/clasificacion.py` (fuente única):

| Clase | Qué es | Ejemplos | Al actualizar |
|-------|--------|----------|---------------|
| **N** núcleo | Reglas, guías, scripts, plantillas de ficha | `REGLAS.md`, `10-guias/*`, `_PLANTILLA.md` | Se reemplaza si el proyecto no lo editó |
| **P** plantilla a rellenar | Se completa en cada proyecto | `00-nucleo/configuracion-proyecto.md`, `ESTADO.md` | Nunca se sobrescribe; se avisa si la plantilla cambió |
| **M** mixto | Índices con filas del proyecto | `*/INDICE.md`, `README.md` | Nunca se sobrescribe |
| **C** contenido | Fichas, instrucciones, rutas, espejo, ADR | `25-areas/*`, `05-instrucciones/**/*.md` | Jamás se toca |

## Cómo se hace cumplir

1. **Huellas:** `uxyngraphar/.uxyngraphar.lock` guarda el hash de cada archivo tal como lo entregó el pack. `python3 uxyngraphar/scripts/verificar-nucleo.py` falla si un archivo N cambió (`NUCLEO-MODIFICADO`), se borró (`NUCLEO-ELIMINADO`), si aparece uno nuevo en zona reservada (`NUCLEO-EXTENDIDO`) o hay archivos fuera de la taxonomía (`FUERA-DE-TAXONOMIA`).
2. **Claude Code:** `instalar-pack.py --proteger` genera reglas `deny` de edición en `.claude/settings.json`.
3. **Cursor (fail-closed):** el mismo `--proteger` escribe `.cursor/uxyngraphar-protegido.json`, la guardia `.cursor/hooks/uxyngraphar-guardia-nucleo.py`, `.cursor/hooks.json` con `failClosed: true` (`preToolUse` + `beforeShellExecution`) y `.cursor/rules/uxyngraphar-nucleo.mdc`. Cualquier intento de editar el núcleo o mutarlo por shell se **niega**; si la guardia falla o no responde JSON válido, también se bloquea.
4. **Filesystem:** archivos clase N, el lock, las carpetas `10-guias/`, `55-automatizaciones/`, `scripts/`, `00-nucleo/` (impide crear archivos nuevos) y los mecanismos (`.cursor/hooks*`, manifiesto, `.claude/settings.json`, CODEOWNERS) quedan **sin bit de escritura**. El IDE no puede guardar ni ampliar el núcleo; solo `actualizar-pack.py` / el panel / `doctor.py --fix` descongelan, escriben y vuelven a congelar. Las plantillas **P** dentro de `00-nucleo/` siguen siendo archivos escribibles.
5. **CODEOWNERS:** bloque de revisión humana sobre el núcleo.
6. **Puerta:** `controlar.py` ejecuta siempre el control `nucleo` en modo **bloqueante** (R-20 no admite `aviso`/`apagado` en `niveles.nucleo`).
7. **Gancho y CI:** `instalar-ganchos.py` ejecuta la verificación en `pre-commit`; el CI la repite (ver [ci-validacion-documentacion.md](../10-guias/ci-validacion-documentacion.md)).

`doctor.py` trata la falta de deny, hooks Cursor, solo lectura o CODEOWNERS como **ERROR**; `doctor.py --fix` regenera esas capas y reaplica el congelado.

## Qué sí fluye

El **contenido** del proyecto (clase C) se actualiza con cada instrucción aprobada. Congelado = las reglas, no el contenido. Las plantillas P siguen editables.

## Cómo proponer mejoras al núcleo

1. Abrir ficha en `46-evolucion-documentacion/01-pendientes/YYYY-MM-DD/` del proyecto (`decisiones.py new evo --slug …`). Es el **único canal**: la 46 de un proyecto es un buzón de propuestas hacia el pack fuente (uxyngraphar), no una cola de trabajo local.
2. El humano decide: aprueba, pospone o rechaza.
3. Si aprueba, el cambio se implementa **en el pack fuente**, se publica una versión nueva y el proyecto la recibe con `actualizar-pack.py` ([actualizar-nucleo.md](../10-guias/actualizar-nucleo.md)).
4. **Sin excepciones locales (R-20):** no existe forma de «aceptar» una edición del núcleo en el proyecto. Si está alterado, el humano lo restaura con `actualizar-pack.py --apply --restaurar-nucleo` (el respaldo conserva la copia alterada).

## Reglas concisas (R-20)

1. El núcleo solo cambia en uxyngraphar y entra con `actualizar-pack.py`.
2. Nadie del proyecto (agente **ni persona**) edita, borra, renombra ni amplía zonas N, ni toca `.uxyngraphar.lock`, `.claude/settings.json`, `.cursor/hooks*`, manifiesto Cursor, `CODEOWNERS`, CI o ganchos.
3. Mejoras → solo ficha EVO en 46.
4. No se evita la verificación (`--no-verify`, `--warn`, `niveles.nucleo` ≠ bloqueante) ni se hace bypass del FS (`chmod +w`) ni de los hooks.
5. Núcleo alterado → parar, avisar, restaurar (humano). Diagnóstico completo: `python3 uxyngraphar/scripts/doctor.py --pack RUTA_PACK`.

## Límites honestos

Las capas anteriores cubren el uso del framework (agentes, personas en el IDE, commits). Quien tenga control total de la máquina puede forzar escritura (p. ej. `sudo chmod`); eso es sabotaje deliberado fuera del protocolo. Las capas independientes (gancho, CI `--contra <pack>`, CODEOWNERS, sello del lock) siguen detectando y bloqueando el resultado.
