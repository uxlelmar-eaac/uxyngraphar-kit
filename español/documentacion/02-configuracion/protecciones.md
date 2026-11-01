# Protecciones

El instalador puede añadir:

- Reglas **deny** para agentes (núcleo de solo lectura)
- `CODEOWNERS`
- Ganchos / checks de commit
- Workflows CI que ejecutan `controlar.py`

## Después de instalar: en el panel

`uxyngraphar` → **Proyecto → Protecciones**:

- **Ganchos de git:** ver si están, «Instalar o reparar», añadir `pre-push` o quitarlos. Viven fuera de git: cada persona los instala en su copia.
- **Quién aprueba los cambios al núcleo:** cambia el propietario de `CODEOWNERS` (con vista previa y copia).
- Reglas deny para agentes, CI y `.gitignore`: si faltan, **Proyecto → Salud → «Arreglar»** las regenera.

## Flags al sembrar (terminal, avanzado)

| Flag | Efecto |
|------|--------|
| `--propietario @usuario` | Rellena CODEOWNERS con ese GitHub user/org |
| `--estricto` | Modo de protección más estricto |
| `--sin-proteger` | **No** añade deny/CODEOWNERS/CI/ganchos |

Sin `--sin-proteger`, el asistente suele ofrecer protecciones (en UI) o aplicar defaults seguros.

## Para qué sirven

Evitan que una IA (u un humano) edite el núcleo del pack a mano y rompa futuras actualizaciones.

## Si algo falla en CI

1. Lee la salida de `controlar.py`
2. No borres el workflow a ciegas
3. Guías: `uxyngraphar/10-guias/control-de-construccion.md`, `uxyngraphar/10-guias/ci-validacion-documentacion.md`
4. En local: panel → **Proyecto → Salud** (o `python3 uxyngraphar/scripts/doctor.py`)
