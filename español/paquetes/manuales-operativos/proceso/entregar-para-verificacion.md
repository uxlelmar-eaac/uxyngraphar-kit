---
fase: entregar-para-verificacion
resuelve: [manuales-desfasados]
skills: []
---

# Fase: entregar-para-verificacion

## Objetivo

Dejar los manuales listos para que una persona los pruebe y los pase a `vigente`.

## Entradas

- Los manuales creados o actualizados.

## Pasos

1. Comprueba que cada manual tocado está en `borrador`. Si actualizaste uno `vigente`, pásalo a borrador: `python3 $P/scripts/comun/fichas.py estado <id> borrador`.
2. Ejecuta `python3 $P/scripts/comun/verificar.py`.
3. Al cerrar, lista a la persona los manuales que tiene que probar y el comando para marcarlos: `python3 $P/scripts/comun/fichas.py estado <id> vigente --humano`, con `ultima_verificacion` a la fecha de la prueba.

## Criterio de salida

- Todos los manuales tocados en `borrador` y `verificar.py` sin errores.
- La persona sabe qué manuales debe probar.
