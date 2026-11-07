---
name: ejecutar-humo
description: Ejecuta las pruebas de humo configuradas por la persona (arranque y flujos básicos contra un entorno de prueba) y lista las que fallan o pasan del tiempo.
resuelve: [flujos-basicos-rotos]
---

# Ejecutar humo

## Cuándo usarla

- La persona pide comprobar que la app arranca o que un flujo básico funciona.
- Solo si hay comandos en `humo` y la persona ha pedido ejecutarlos.

## Pasos

1. Lee `humo` en los ajustes efectivos. Cada entrada es `{"nombre": "…", "comando": "…", "segundos": 300}`; sin entradas, `vivas.py` da la nota `sin pruebas de humo en ajustes`.
2. Comprueba que cada comando apunta a un entorno de prueba o simulación (límite 3). Ante la duda, pregunta y no ejecutes.
3. Sin `--ejecutar`, `python3 $P/scripts/vivas.py humo` solo dice cuántas hay sin ejecutar. Para ejecutarlas: `python3 $P/scripts/vivas.py humo --ejecutar`.
4. Cada comando corre desde la raíz de la app con su límite de `segundos`. Falla si sale con código distinto de 0 (`alta: humo «arranque» falla (código 3): <última línea>`) o si pasa del tiempo (`alta: humo «arranque» excede el tiempo`).
5. No añadas ni cambies comandos de `humo`: son de la persona.

## Resultado

- Las pruebas de humo que fallan, con el código de salida y la última línea de su salida.
