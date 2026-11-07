---
name: preparar-exportacion
description: Revisa que las EVO aprobadas estén completas y sin datos del proyecto que no deban salir, y da a la persona el comando de exportación (que solo ella puede ejecutar).
resuelve: [propuestas-sin-llegar-al-catalogo]
---

# Preparar exportación

## Cuándo usarla

- En la fase `llevar-al-catalogo`.
- Cuando la persona pregunta qué EVO están listas para el catálogo.

## Pasos

1. Lista las aprobadas: `python3 $P/scripts/comun/fichas.py listar evo --status approved`. Las que ya tienen `exportada` con fecha salieron en una exportación anterior: dilo.
2. Ejecuta `python3 $P/scripts/verificar-evolucion.py` y resuelve en las fichas los avisos de secciones vacías o paquetes no instalados.
3. Lee cada EVO buscando datos que no deban salir del equipo (nombres de clientes, credenciales, URLs internas). El script quita rutas absolutas, no esto: propón a la persona redactarlos antes de exportar.
4. Dale a la persona el comando: `python3 $P/scripts/evolucion.py exportar --humano` (con `--todas` incluye las `pending`). Sin `--humano` el script se niega.

## Resultado

- Lista de EVO listas para exportar, avisos resueltos y la persona con el comando.
