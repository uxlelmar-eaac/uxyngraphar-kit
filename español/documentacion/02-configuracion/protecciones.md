# Protecciones

El instalador puede añadir:

- Reglas **deny** para agentes (núcleo de solo lectura)
- `CODEOWNERS`
- Ganchos / checks de commit
- Workflows CI que ejecutan `controlar.py`

## Flags al sembrar

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
3. Guías: `docs/10-guias/control-de-construccion.md`, `docs/10-guias/ci-validacion-documentacion.md`
4. En local: `python3 docs/scripts/doctor.py` (± `--fix`)
