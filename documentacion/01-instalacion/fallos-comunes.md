# Fallos comunes

## `uxyngraphar: command not found`

1. Abre una terminal nueva.
2. `uxyngraphar version`
3. Revisa PATH / `--sin-path` / `UXYNGRAPHAR_HOME` → [herramienta.md](herramienta.md)

## Sembré `ambos` y las carpetas no son las mías

Con `--si`, el default puede ser `apps/api` + `apps/web`. Vuelve a instalar con `--mismo-repo` y `--sub-servidor` / `--sub-cliente` correctos (o dos repos con `--proyecto2`). → [../06-packs/monorepo.md](../06-packs/monorepo.md)

## Doctor falla

→ [../02-configuracion/doctor.md](../02-configuracion/doctor.md) (`--fix` solo si lo indica).

## Actualizar dice “salto mayor”

→ [../03-uso-humano/actualizar.md](../03-uso-humano/actualizar.md) (`--migracion-aprobada`).

## Quiero quitar uxyngraphar del proyecto

1. `uxyngraphar proyectos --quitar RUTA` (opcional)
2. Elimina del git lo que ya no quieras (`docs/`, `AGENTES.md`, protecciones) con revisión humana
3. `uxyngraphar desinstalar` solo quita la **herramienta** del equipo, no el pack

## Windows: `python3` no existe

Usa `py -3` o `python`.
