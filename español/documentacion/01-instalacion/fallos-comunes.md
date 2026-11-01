# Fallos comunes

## `uxyngraphar: command not found`

1. Abre una terminal nueva.
2. `uxyngraphar` (debe abrir el panel)
3. Revisa PATH / `--sin-path` / `UXYNGRAPHAR_HOME` → [herramienta.md](herramienta.md)

## Sembré `ambos` y las carpetas no son las mías

Con `--si`, el default puede ser `apps/api` + `apps/web`. Vuelve a instalar con `--mismo-repo` y `--sub-servidor` / `--sub-cliente` correctos (o dos repos con `--proyecto2`). → [../06-packs/monorepo.md](../06-packs/monorepo.md)

## La salud del proyecto marca errores

Panel → **Proyecto → Salud**: cada problema trae su arreglo; «Arreglar» aplica los seguros con copia antes. → [../02-configuracion/doctor.md](../02-configuracion/doctor.md)

## Actualizar dice “salto mayor”

→ [../03-uso-humano/actualizar.md](../03-uso-humano/actualizar.md) (`--migracion-aprobada`).

## Quiero quitar uxyngraphar del proyecto

1. Panel → **Mis proyectos** → «Quitar» (opcional)
2. Elimina del git lo que ya no quieras (`uxyngraphar/`, `AGENTES.md`, protecciones) con revisión humana
3. Panel → **Sistema → Desinstalar** solo quita la **herramienta** del equipo, no el pack

## Windows: `python3` no existe

Usa `py -3` o `python`.
