# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/mensajes-de-commit`.

## `scripts/commits.py`

- `python3 $P/scripts/commits.py --mensaje "feat(orders): add coupon discount"`: comprueba un mensaje antes de hacer el commit (solo su primera línea, el asunto). Código 0 = válido.
- `python3 $P/scripts/commits.py <n>`: revisa los últimos `n` commits sin merges.
- `python3 $P/scripts/commits.py`: revisa los últimos `commits_revisar` (20 por defecto).

Qué detecta: asuntos fuera de Conventional Commits (tipo de la lista, ámbito en minúsculas, `: ` y resumen), con caracteres no ASCII o de más de 72 caracteres. Imprime una línea por problema (`commit <sha>: «…» no cumple Conventional Commits en inglés ASCII (≤72 caracteres)`) y un resumen; código 0 = sin problemas, 1 = hay problemas. Fuera de un repositorio git no revisa nada y sale con 0.

No está en «verificaciones»: el historial antiguo de un proyecto puede no cumplir la convención. Se ejecuta en la fase `preparar-commit` sobre los commits nuevos.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
