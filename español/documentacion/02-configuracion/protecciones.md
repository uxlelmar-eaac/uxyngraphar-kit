# Protecciones

El instalador puede añadir:

- Reglas **deny** para agentes Claude (núcleo de solo lectura)
- Hooks **Cursor fail-closed** (`.cursor/hooks.json` + guardia) y regla `.cursor/rules/uxyngraphar-nucleo.mdc`
- Manifiesto `.cursor/uxyngraphar-protegido.json`
- Archivos del núcleo en **solo lectura** en disco
- `CODEOWNERS`
- Ganchos / checks de commit
- Workflows CI que ejecutan `controlar.py`

## Después de instalar: en el panel

`uxyngraphar` → **Proyecto → Protecciones**:

- **Ganchos de git:** ver si están, «Instalar o reparar», añadir `pre-push` o quitarlos. Viven fuera de git: cada persona los instala en su copia.
- **Quién aprueba los cambios al núcleo:** cambia el propietario de `CODEOWNERS` (con vista previa y copia).
- Deny Claude, hooks Cursor, CI y `.gitignore`: si faltan, **Proyecto → Salud → «Arreglar»** las regenera (y reaplica el congelado en disco).

## Flags al sembrar (terminal, avanzado)

| Flag | Efecto |
|------|--------|
| `--propietario @usuario` | Rellena CODEOWNERS con ese GitHub user/org |
| `--estricto` | Modo de protección más estricto |
| `--sin-proteger` | **No** añade deny/hooks Cursor/CODEOWNERS/CI/ganchos/FS |

Sin `--sin-proteger`, el asistente suele ofrecer protecciones (en UI) o aplicar defaults seguros.

## Para qué sirven

Hacen del núcleo un **framework rígido**: ni agentes ni personas del proyecto lo editan a mano. Solo se actualiza con `actualizar-pack` / el panel. Faltas de protección = ERROR en el doctor.

## Si algo falla en CI

1. Lee la salida de `controlar.py`
2. No borres el workflow a ciegas
3. Guías: `uxyngraphar/10-guias/control-de-construccion.md`, `uxyngraphar/10-guias/ci-validacion-documentacion.md`
4. En local: panel → **Proyecto → Salud** (o `python3 uxyngraphar/scripts/doctor.py`)
