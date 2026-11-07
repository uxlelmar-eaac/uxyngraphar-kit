---
fase: preparar-commit
resuelve: [commits-sin-convencion]
skills: [redactar-commit, revisar-commits]
---

# Fase: preparar commit

## Objetivo

Que cada commit del cambio tenga un mensaje en Conventional Commits, en inglés ASCII y de una sola intención, y que la rama, si es nueva, siga `tipo/descripcion-corta`.

## Entradas

- El cambio terminado y verificado (con las verificaciones de los demás paquetes activos).
- Los últimos mensajes del repositorio, como referencia de ámbitos (`git log --oneline -n 20`).

## Pasos

1. Separa el cambio por intención: un arreglo y una función nueva son dos commits (`git add -p` si comparten archivo).
2. Si la rama es nueva, nómbrala `tipo/descripcion-corta` en inglés (`feat/checkout-coupons`).
3. Aplica la skill `redactar-commit` para cada commit: el asunto se comprueba con `commits.py --mensaje` antes de hacer el commit.
4. Tras hacer los commits, aplica la skill `revisar-commits` con `n` = número de commits nuevos: `python3 $P/scripts/commits.py <n>`.
5. Si un commit tuyo no pasa, corrige su mensaje antes de publicarlo (`git commit --amend` solo sobre commits locales tuyos). Los mensajes antiguos de otras personas no se reescriben.

## Criterio de salida

- `commits.py <n>` sobre los commits nuevos sale con código 0.
- La rama nueva, si la hay, sigue `tipo/descripcion-corta`.
