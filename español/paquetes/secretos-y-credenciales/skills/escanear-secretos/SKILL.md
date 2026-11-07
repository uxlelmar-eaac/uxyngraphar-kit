---
name: escanear-secretos
description: Ejecuta secretos.py sobre unas rutas, sobre las raíces o sobre lo que git versiona, e interpreta cada hallazgo (por contenido o por nombre de archivo) sin revelar el valor.
resuelve: [secretos-en-el-codigo, archivos-de-secretos-versionados]
---

# Escanear secretos

## Cuándo usarla

- Al empezar (fase `diagnosticar`) y al terminar (fase `escanear`) un cambio.
- Antes de proponer un commit.
- Cuando la persona pide revisar si hay secretos en el repositorio.

## Pasos

1. Elige el alcance:
   - Unas rutas: `python3 $P/scripts/secretos.py <ruta>…`.
   - Todo: `python3 $P/scripts/secretos.py` (usa `raices` de los ajustes).
   - Lo que irá en un commit: `python3 $P/scripts/secretos.py --git` (versionado, preparado o sin seguimiento no ignorado). Fuera de un repositorio git sale con código 2.
2. Añade `--informe` si la persona quiere constancia: guarda `uxyngraphar/trabajo/secretos-y-credenciales/informes/escaneo-<fecha>.md`.
3. Lee cada línea:
   - `<ruta>: archivo de secretos (por nombre); no debe versionarse` → `.env`, `*.pem`, `credentials.json`… No lo abras.
   - `<ruta>:<línea>: <tipo> (<muestra>)` → patrón por contenido; la muestra ya va enmascarada (`sk_l…(32 car.)`).
4. La última línea resume: `secretos: N archivos revisados, M hallazgos`. Código 0 = limpio; 1 = hay hallazgos.
5. Ten en cuenta lo que no se marca: líneas con placeholders conocidos (`<…>`, `example`, `changeme`, `process.env`, `os.environ`…), líneas con la marca `uxyngraphar:permitir-secreto` y, en rutas de prueba (`tests/`, `*.spec.ts`, `test_*.py`…), la heurística de «credencial asignada». Los patrones fuertes (AWS, GitHub, Stripe, llaves privadas, JWT) se detectan en cualquier ruta.

## Resultado

- Lista de hallazgos por ruta y línea, separados en tuyos y heredados, sin ningún valor completo.
