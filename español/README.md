# uxyngraphar

**uxyngraphar** (contrato escrito firmado y sellado por todas las partes) es un **sistema documental de gobernanza humano–IA**: el *contrato* que ata a la IA y el *espejo* que la mantiene fiel al código.

Este repositorio contiene las **dos variantes** del pack (en español):

| Pack | Rol | Entrada |
|------|-----|---------|
| [`backend/`](backend/README.md) | Servidor / API — fuente de verdad de `15-rutas/` | [`AGENTES.md`](backend/AGENTES.md) |
| [`frontend/`](frontend/README.md) | Cliente / UI | [`AGENTES.md`](frontend/AGENTES.md) |

Cada variante es un pack **autosuficiente**: el asistente lo instala en `docs/` del repositorio objetivo y allí vive de forma independiente. Alias de entrada por stack: [`AGENTES.md`](AGENTES.md).

## Instalar en una línea

Una sola vez por equipo, instala la herramienta `uxyngraphar` (solo necesita Python 3.10+; para sembrar el pack en un proyecto, también git):

```bash
# Linux / macOS
curl -fsSL https://github.com/uxlelmar-eaac/uxyngraphar/releases/latest/download/instalar-uxyngraphar.py | python3 -
```

```powershell
# Windows (PowerShell); si no tienes el lanzador «py», usa «python» en su lugar
irm https://github.com/uxlelmar-eaac/uxyngraphar/releases/latest/download/instalar-uxyngraphar.py | py -
```

- **Al terminar se abre el panel en tu navegador** (solo en tu equipo) con todo lo que pasó en la terminal y lo que queda por decidir: añadir el comando al PATH, tu plantilla de configuración e instalar en tu primer proyecto. Sin escritorio, en CI o con `--consola`, todo sigue en la terminal.
- **Versión fija:** cambia `latest/download` por `download/v1.0.0`. Opciones del instalador detrás de `python3 -`: `--version X.Y.Z`, `--sin-path`, `--consola`.
- **Revisar antes de ejecutar:** `curl -fsSL <url> -o instalar-uxyngraphar.py`, léelo y luego `python3 instalar-uxyngraphar.py`.
- **Dónde queda:** `~/.uxyngraphar/` (Windows: `%LOCALAPPDATA%\uxyngraphar\`; cambia con `UXYNGRAPHAR_HOME`) y el comando en `~/.local/bin/uxyngraphar` (Windows: `%LOCALAPPDATA%\uxyngraphar\bin\uxyngraphar.cmd`, generado al instalar). Si hace falta, añade esa carpeta al PATH (bloque marcado en tu `.bashrc`/`.zshrc`, o PATH de usuario en Windows). Nunca pide `sudo`.
- **Seguridad:** descarga por HTTPS, comprueba la huella SHA256 de la versión antes de escribir nada, rechaza rutas peligrosas del zip y, si la descarga se corta, el instalador no ejecuta nada. Volver a ejecutarlo es seguro.

### Uso diario

| Comando | Qué hace |
|---------|----------|
| `uxyngraphar panel` | **Panel en el navegador:** tus proyectos (versión, salud, actualizar, instalar), la configuración de cada uno con vista previa y copia de seguridad, colaborar Sí/No, y tu **plantilla** de configuración para proyectos nuevos. |
| `uxyngraphar instalar [RUTA]` | Siembra el pack en un proyecto. Sin argumentos abre la pantalla del navegador; con `RUTA` u opciones (`--pack`, `--si`…) funciona en texto. Registra el proyecto. |
| `uxyngraphar actualizar [RUTA…]` · `--todos` | Lleva proyectos a la versión de la herramienta: simula, respalda en `.uxyngraphar-respaldo/`, toca solo el núcleo y deja los conflictos como `*.uxyngraphar-nuevo`. |
| `uxyngraphar estado [RUTA]` | Versión del proyecto, de la herramienta y la última publicada. |
| `uxyngraphar proyectos` | Proyectos registrados en este equipo (`--agregar RUTA`, `--quitar RUTA`, `--salud`). |
| `uxyngraphar configuracion [RUTA]` | El archivo de configuración del proyecto (`docs/uxyngraphar.config.json`): cómo queda y qué valores son inválidos. Para editarlo en pantalla: `uxyngraphar panel`. Guía: `docs/10-guias/configuracion-uxyngraphar.md`. |
| `uxyngraphar autoactualizar` | Descarga la última versión de la herramienta. No cambia ningún proyecto. |
| `uxyngraphar usar X.Y.Z` · `version` · `desinstalar` | Cambiar de versión, ver las guardadas, o quitar la herramienta (los proyectos no se tocan). |

### Colaborar en la mejora (libre)

Al instalar (y una vez al actualizar un proyecto que aún no respondió) el asistente pregunta **«¿Te gustaría colaborar en la mejora de uxyngraphar?»** con Sí y No, sin opción marcada, y antes muestra qué sale y qué no. Con **Sí**, las fichas EVO nuevas o cambiadas (`docs/46-evolucion-documentacion/`) se envían solas al terminar cada `instalar` o `actualizar` que hagas tú; nunca desde CI, ganchos ni el agente, y nunca código, rutas, correos ni métricas de uso. Con **No**, no se envía nada. Se cambia cuando quieras con `feedback.py activar` o `revocar`. Sin pantalla: `--colaborar si|no`. El receptor oficial es el backend de uxyngraphar (repo `uxyngraphar-backend`). Guía: `10-guias/envio-sugerencias.md`.

Cada proyecto lleva su copia del pack en `docs/` (va en git) y su versión en `docs/.uxyngraphar.lock`, así que pueden convivir proyectos en versiones distintas y quien clona el proyecto no necesita la herramienta.

## Instalar desde un clon (sin la herramienta)

En cualquier sistema (Windows, macOS o Linux): `python3 instalar.py` (en Windows también `py -3 instalar.py`). Se abre una pantalla en tu navegador (solo en tu equipo) con 4 pasos: tu proyecto, qué instalar y dónde (servidor, cliente o ambos; un repo o dos), protección, y un **plan exacto antes de escribir nada**. Cada opción explica qué cambia si la eliges. Al terminar muestra lo que se hizo y qué sigue. Si el proyecto ya tiene uxyngraphar, ofrece actualizar sin tocar tu contenido. Requiere Python 3.10+ y git. Para terminales sin navegador: `python3 instalar.py --consola`.

## Actualizar desde un clon (sin la herramienta)

En cualquier sistema: `python3 actualizar.py [RUTA_PROYECTO]` (en Windows también `py -3 actualizar.py`). Se abre una pantalla en tu navegador (solo en tu equipo) con 3 pasos: eliges uno o varios proyectos (detecta los packs instalados, también en monorepos), **revisas qué cambiaría** agrupado en lenguaje llano (archivos nuevos, actualizados, los que necesitan tu decisión con **comparación línea a línea**, plantillas con novedades, estado de salud) y confirmas. Antes de escribir hace copia de seguridad en `.uxyngraphar-respaldo/`, actualiza solo el núcleo (tu contenido no se toca) y añade las protecciones nuevas (CI, reglas de agentes, `.gitignore`…). Un salto de versión mayor pide el id de una instrucción aprobada. Para terminales sin navegador: `python3 actualizar.py RUTA --consola`; para scripts: `--si`.

## Qué incluye cada pack

Instrucciones como contrato de tarea, reglas del proyecto propias del equipo (`96-reglas-proyecto/`, se aplican sin tocar las del núcleo), presupuesto de tokens, ciclo vinculante de actos, espejo 1:1 del código (`50-sistema-integral/`), colas de mejoras y evolución (`45`/`46`), herramientas autorizadas (`35`) y un panel de decisiones pendientes en Python (solo stdlib). Detalle completo en el `README.md` de cada pack.

## Estructura

```text
español/
├── uxyngraphar.py                         # la herramienta «uxyngraphar» (instalar, actualizar, estado, proyectos…)
├── instalar.py                            # instalar en un proyecto (todas las plataformas)
├── actualizar.py                          # actualizar proyectos existentes (todas las plataformas)
├── instalador/                            # asistente y panel (pantalla web local + consola) e instalador de una línea (arranque*.py)
├── AGENTES.md                             # alias de entrada (apunta al pack del stack)
├── backend/                               # pack servidor/API (se instala como docs/)
├── frontend/                              # pack cliente/UI (se instala como docs/)
└── _compartido/                           # fuente de lo idéntico en ambos packs + construir-packs.py + publicar.py
```

## Mantener los packs (repo fuente)

- Lo idéntico en ambos packs se edita **solo** en `_compartido/base/` y se copia con `python3 _compartido/construir-packs.py` (`--verificar` en CI falla si hay deriva).
- Pruebas: `python3 backend/scripts/ejecutar-pruebas.py` y `python3 -m unittest discover -s instalador -p "test_*.py"` · `python3 -m unittest discover -s _compartido -p "test_*.py"`.
- **Solo Python para ejecutables:** todo script, instalador, actualizador o gancho de git del proyecto se escribe en Python (solo biblioteca estándar) para que funcione igual en Windows, macOS y Linux. No se añaden `.sh`, `.bat`, `.cmd`, `.ps1`, `.command` ni `.vbs`; en Windows se ejecutan con `py -3 <script>.py` o `python <script>.py`.
- **Reglas para que ninguna versión rompa una actualización** (ver la sección «Garantías» de `10-guias/actualizar-nucleo.md`):
  1. No quitar ni renombrar un script u opción de `scripts/nucleo/contrato.py`: la lista solo crece; un renombre deja el nombre viejo como alias.
  2. Si una versión cambia algo que los proyectos ya tienen (una clave de `uxyngraphar.config.json`, un archivo que se mueve), lo hace con una migración en `scripts/nucleo/migraciones.py` (idempotente, con prueba), nunca pidiéndoselo a la persona.
  3. Una sección nueva de la configuración entra con un valor por defecto que no cambia nada (`10-guias/configuracion-uxyngraphar.md` § «Cómo crece»).
  4. Antes de etiquetar: `python3 _compartido/probar-actualizaciones.py` (lo repite el CI): actualiza desde cada versión publicada y falla si algo se rompe.
- Al publicar: subir `VERSION.md` + `CHANGELOG.md` (en `_compartido/base/`), reconstruir, hacer commit y etiquetar `vX.Y.Z` (`git tag vX.Y.Z && git push origin vX.Y.Z`). El workflow `.github/workflows/publicar.yml` pasa las pruebas en Linux, macOS y Windows, ejecuta `_compartido/publicar.py` (zip, instalador de una línea y `SHA256SUMS`) y crea la release: desde ese momento el comando de una línea instala esa versión. El repositorio debe ser público. Para probar la publicación en local: `python3 _compartido/publicar.py --salida dist`.

## Licencia

Copyright © 2026 uxleleaac / uxlelmar

Este kit (documentación y herramienta de packs) se publica bajo **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**.

- Texto legal (raíz del repo): [`../LICENSE`](../LICENSE) · resumen [`../LICENCIA.md`](../LICENCIA.md) · [`../LICENSING.md`](../LICENSING.md)
- El código de la app (backend/frontend) usa **GPL-3.0** con licencia comercial opcional; no confundir con este kit.

## Versión

La versión vigente de cada pack vive en su [`VERSION.md`](backend/VERSION.md) — **fuente única** — y su historial en el `CHANGELOG.md` del pack. Ambos packs se versionan en espejo.

## Gobernanza

- Estructura del pack **intocable por IA** sin instrucción `approved` derivada de una ficha `EVO-*` (regla R-14).
- Paridad entre packs: [`PARIDAD-PACKS.md`](backend/PARIDAD-PACKS.md) + `python3 scripts/verificar-paridad.py` (solo en este repo; no se instala en proyectos).
- Validación documental: `python3 scripts/validar-documentacion.py` (ver `10-guias/ci-validacion-documentacion.md`).
