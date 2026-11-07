---
name: proponer-ajuste-local
description: Propone un ajuste local que, solo en este proyecto, sustituye un paso o una regla de un archivo concreto de otro paquete instalado, sin editar ese paquete.
resuelve: [paquetes-sin-adaptar-al-proyecto]
---

# Proponer ajuste local

## Cuándo usarla

- Un paso de otro paquete instalado no encaja en este proyecto (un comando que aquí no existe, una carpeta distinta).
- La persona quiere probar un cambio en un paquete antes de llevarlo al catálogo.

## Pasos

1. Comprueba que el archivo existe: `uxyngraphar/paquetes/<id>/<archivo>` (por ejemplo `proceso/preparar-commit.md` o `README.md`).
2. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva ajuste --slug <slug>`. Nace `propuesto` en `uxyngraphar/trabajo/adaptaciones-de-paquetes/ajustes-locales/`.
3. Rellena `paquete` (id del paquete instalado) y `aplica_a` (archivo relativo a su carpeta). Deja `huella: null`: la escribe la aprobación. Si hay una ficha EVO de `evolucion-del-sistema` que lo origina, cítala en `evo`.
4. En «Qué cambia», concreta qué paso o regla se sustituye y por qué texto; en «Cuándo retirarlo», la versión del paquete o la EVO que lo hará innecesario.
5. Ejecuta `python3 $P/scripts/verificar-adaptaciones.py`: un `paquete` vacío o un archivo que no existe salen como aviso.
6. Di a la persona que lo activa con `python3 $P/scripts/adaptaciones.py aprobar-ajuste AJL-… --humano`, que además guarda la huella del archivo.
7. Si el cambio vale para todos los proyectos, propón también una ficha en `evolucion-del-sistema`.

## Resultado

- Una ficha `AJL-…` en `propuesto` que apunta a un archivo existente de un paquete instalado.
