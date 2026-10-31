# Elegir pack — qué pack instalar en cada aplicación

Hay dos packs con el mismo núcleo (reglas, scripts, puerta de control) y documentación orientada a un rol. Elige por **qué construye el repositorio**, no por el lenguaje.

| Si el repositorio es… | Pack |
|-----------------------|------|
| API, servicio, worker, CLI, librería, ETL, pipeline de datos, bot | **servidor** (`backend`) |
| Web, móvil, escritorio, extensión, front de un monorepo (UI + estado + contratos con la API) | **cliente** (`frontend`) |
| Monorepo con ambos | un pack por app, cada uno con su `AGENTES.md` junto a su `docs/` (`apps/api/docs` y `apps/web/docs`); ver «Escenarios» abajo |
| Aplicación sin separación clara (fullstack en un solo árbol) | **servidor** si la lógica de negocio manda; añade el otro con `--docs` distinto solo si hay equipos separados |

## Instalar

```bash
python3 español/backend/scripts/instalar-pack.py español/backend --repo . --proteger --propietario @mi-org/mantenedores
python3 docs/scripts/doctor.py          # diagnóstico
python3 docs/scripts/instalar-ganchos.py
```

`instalar-pack.py` detecta la pila y escribe `docs/uxyngraphar.config.json` ([control-de-construccion.md](control-de-construccion.md)). Para un repositorio con documentación previa: `--analizar` primero y `--adoptar` después ([adopcion-pack.md](adopcion-pack.md)). Actualizar: [actualizar-nucleo.md](actualizar-nucleo.md).

## Escenarios de instalación

| Escenario | Cómo |
|-----------|------|
| Solo servidor o solo cliente | Asistente (`instalar.py` / doble clic) o `instalar-pack.py <pack> --repo .` |
| Ambos, **repos distintos** | Una instalación por repo, cada una con su pack y `docs/` en la raíz. `python3 instalar.py --pack ambos --proyecto <repo-api> --proyecto2 <repo-web>` lo hace en una pasada |
| Ambos, **mismo repo** | `python3 instalar.py --pack ambos --mismo-repo --sub-servidor apps/api --sub-cliente apps/web`; o a mano: `instalar-pack.py <pack> --repo . --docs apps/api/docs` y lo mismo con el otro |
| Una app dentro de un monorepo | `--docs <carpeta-app>/docs` |

Reglas del modo monorepo: la carpeta del pack se llama siempre `docs`; `AGENTES.md`, `AGENTS.md` y `CLAUDE.md` se instalan **junto a `docs/`** (el agente trabaja en la carpeta de su app y sus rutas `docs/…` se resuelven desde ahí); cada pack tiene su `.uxyngraphar.lock`, su `uxyngraphar.config.json` (el control solo mira el código de su app) y su bloque de `CODEOWNERS`; el gancho `pre-commit` vigila todos los packs del repo. En CI ejecuta `controlar.py --base origin/main --docs <docs>` una vez por pack. Actualizar y diagnosticar también son por pack: `actualizar-pack.py <pack> --docs apps/api/docs`, `doctor.py --docs apps/api/docs`.

## Qué es común y qué cambia

Común (idéntico, fuente `_compartido/` del repo uxyngraphar): todos los scripts, la puerta de control, las reglas R-01…R-24, el ciclo de instrucciones, el espejo y la distribución. Específico: `AGENTES.md`, plantillas y guías con terminología del rol (contratos de API vs. pantallas/estado), rutas y áreas.

## Un rol nuevo

Se crea la carpeta del pack con lo específico y se añade a `PACKS` en `_compartido/construir-packs.py`; todo lo común llega solo. Cambios en plantillas o estructura siguen R-14 (ficha `EVO-*` aprobada).
