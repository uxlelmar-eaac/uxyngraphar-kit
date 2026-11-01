# Referencia CLI

En Windows, si no tienes `python3`, usa `py -3` (o `python`) en lugar de `python3`. Tras instalar la herramienta, abre una **terminal nueva** si `uxyngraphar` no se encuentra (PATH).

## Herramienta `uxyngraphar`

| Comando | Qué hace |
|---------|----------|
| `uxyngraphar` · `uxyngraphar ayuda` | Ayuda: los comandos agrupados (Empezar, Tus proyectos, La herramienta) |
| `uxyngraphar ayuda COMANDO` | Sintaxis completa y opciones de ese comando |
| `uxyngraphar panel` | Panel local en el navegador |
| `uxyngraphar panel --bienvenida` | Panel tras el instalador de una línea |
| `uxyngraphar instalar [RUTA]` | Siembra el pack (sin args → UI) |
| `uxyngraphar actualizar [RUTA…]` | Actualiza el núcleo |
| `uxyngraphar actualizar --todos` | Actualiza todos los proyectos registrados |
| `uxyngraphar estado [RUTA]` | Versiones (proyecto / herramienta / última) |
| `uxyngraphar proyectos` | Lista registro local |
| `uxyngraphar proyectos --agregar RUTA` | Registra un proyecto |
| `uxyngraphar proyectos --quitar RUTA` | Quita del registro (no borra `uxyngraphar/`) |
| `uxyngraphar proyectos --salud` | Salud rápida |
| `uxyngraphar configuracion [RUTA]` | Muestra/valida `uxyngraphar.config.json` |
| `uxyngraphar mover-carpeta [RUTA]` | Mueve el pack de `docs/` a `uxyngraphar/` (proyectos anteriores a 1.1.0; muestra el plan y pregunta) |
| `uxyngraphar mover-carpeta [RUTA] --si` | Mueve sin preguntar · `--a docs` para volver |
| `uxyngraphar autoactualizar` | Actualiza la herramienta |
| `uxyngraphar autoactualizar --version X.Y.Z` | Fija versión de la herramienta |
| `uxyngraphar usar X.Y.Z` | Cambia a una versión ya guardada |
| `uxyngraphar version` | Versión actual de la herramienta |
| `uxyngraphar desinstalar` | Quita la herramienta del equipo |
| `uxyngraphar desinstalar --si` | Sin confirmación |

**Colores:** la herramienta y los instaladores usan color y las marcas ✓ (hecho), ! (aviso) y ✕ (error) solo cuando escriben en una terminal. Para desactivar el color define `NO_COLOR=1`; si la terminal no puede mostrar ✓/✕, se usan `+`/`x`. `uxyngraphar autoactualizar` ya no abre el panel cuando no hay versión nueva que instalar.

**Importante:** `desinstalar` **no** elimina el pack de tus repos. Solo borra `~/.uxyngraphar/` (o `%LOCALAPPDATA%\uxyngraphar\`). Para dejar de usar el pack en un proyecto, quita `uxyngraphar/` / `AGENTES.md` a mano y, si hace falta, `proyectos --quitar`.

### Flags comunes de `instalar` / `actualizar`

| Flag | Significado |
|------|-------------|
| `--consola` | Todo en terminal (sin navegador) |
| `--si` | No preguntar; defaults. **Sin `--colaborar`, cuenta como No** a sugerencias EVO; en CI o con un agente (`CI`, `CLAUDECODE`, `UXYNGRAPHAR_AGENTE`…) la pregunta queda pendiente para la persona |
| `--colaborar si\|no` | Respuesta explícita a colaborar |
| `--pack servidor\|cliente\|ambos` | Qué sembrar (`instalar`) |
| `--proyecto RUTA` | Raíz del proyecto (`instalar.py`) |
| `--proyecto2 RUTA` | Segundo repo (cliente) si `--pack ambos` en **repos distintos** |
| `--mismo-repo` | `--pack ambos` en **un solo** repositorio |
| `--sub-servidor DIR` | Subcarpeta del servidor (default típico en auto: `apps/api`; `""` = raíz) |
| `--sub-cliente DIR` | Subcarpeta del cliente (default típico: `apps/web`; `""` = raíz) |
| `--propietario @user` | GitHub user/org para CODEOWNERS |
| `--estricto` | Protecciones estrictas |
| `--sin-proteger` | No añadir deny/CODEOWNERS/CI/ganchos |

## Desde el clon (`español/`)

```bash
python3 instalar.py …          # Windows: py -3 instalar.py …
python3 actualizar.py …
python3 uxyngraphar.py …
```

Mismos flags que arriba. `actualizar.py` también acepta `--consola`, `--si`, `--colaborar`, rutas y (vía herramienta) `--todos`.

## Instalador de una línea (herramienta)

```bash
python3 instalar-uxyngraphar.py --version X.Y.Z --sin-path --consola
```

| Flag | Significado |
|------|-------------|
| `--version X.Y.Z` | Versión concreta |
| `--sin-path` | No tocar PATH ni perfiles de shell |
| `--consola` | No abrir el panel al terminar |

Variables útiles: `UXYNGRAPHAR_HOME`, `UXYNGRAPHAR_SIN_PATH`.

## Scripts frecuentes **dentro del proyecto** (tras sembrar)

```bash
python3 uxyngraphar/scripts/doctor.py [--fix] [--strict] [--json] [--pack RUTA]
python3 uxyngraphar/scripts/decisiones/decisiones.py scan
python3 uxyngraphar/scripts/feedback.py estado|previsualizar|activar|enviar|revocar
python3 uxyngraphar/scripts/actualizar-pack.py RUTA_PACK --apply [--migracion-aprobada ID]
```

En monorepo con subcarpetas, el `uxyngraphar/` puede estar en `apps/api/uxyngraphar/` o `apps/web/uxyngraphar/`: ajusta la ruta.
