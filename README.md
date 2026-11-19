# uxyngraphar

Catálogo de **sistemas especializados** humano–IA (portátiles e inmutables) y la herramienta que los instala en tus repos. Por ahora solo en español.

Cada sistema es un entorno de trabajo completo para un conjunto acotado de problemas: qué resuelve y qué no, límites, proceso por fases, skills, herramientas, andamiaje y ejemplos, todo en su carpeta. Una base común (`sistemas-de-gobernanza/_base/`) es el protocolo que rige la estructura de todos sin limitar su contenido.

Dos numeraciones: la **herramienta** sigue semver (`español/motor/VERSION`, la de las releases) y el **protocolo de sistemas** va por su versión 1 ([`ESPECIFICACION.md`](./español/motor/ESPECIFICACION.md)), que solo cambia si un sistema válido deja de serlo.

Todo está en **`español/`**: el catálogo en `sistemas-de-gobernanza/` (cada sistema independiente) y todo lo demás en [`motor/`](./español/motor/README.md), con el contrato en [`ESPECIFICACION.md`](./español/motor/ESPECIFICACION.md) y el criterio de diseño en [`GUIA-DE-SISTEMAS.md`](./español/motor/GUIA-DE-SISTEMAS.md).

```bash
# Linux / macOS
curl -fsSL https://github.com/uxlelmar-eaac/uxyngraphar-kit/releases/latest/download/instalar-uxyngraphar.py | python3 -
```

```powershell
# Windows (PowerShell)
irm https://github.com/uxlelmar-eaac/uxyngraphar-kit/releases/latest/download/instalar-uxyngraphar.py | py -
```

¿Quieres verificar el instalador antes de ejecutarlo? Ver la vía verificable en [`SECURITY.md`](./SECURITY.md#vía-verificable-recomendada-en-equipos-con-datos-sensibles); con la CLI de GitHub (`gh`) disponible, el instalador además comprueba la procedencia de lo que descarga.

En Windows se usa `py` (el lanzador de Python que instala python.org); si no lo tienes, cambia `py` por `python`. La línea no ejecuta ningún script de PowerShell (`irm` solo descarga el texto y se lo pasa a Python), así que no depende de la política de ejecución.

El instalador llega **vacío**: los sistemas de gobernanza se guardan en el servidor de uxyngraphar y los traes cuando los necesitas, desde el panel (área **Mercado**) o con `uxyngraphar buscar <texto>` e `uxyngraphar instalar <id>`. Lo que traes queda guardado en tu equipo y sigue funcionando sin red. Quien escribe sistemas los publica con `uxyngraphar publicar <id>` (con la sesión de tu cuenta). Ver [ADR 0007](./decisiones/0007-sistemas-en-el-servidor.md).

El instalador te pregunta si quieres un acceso directo en el menú de inicio, el escritorio o la barra de tareas. Después, el único comando que necesitas es **`uxyngraphar`** (o ese acceso directo): abre el panel en tu navegador. El panel se organiza en **Inicio**, **Taller**, **Mis sistemas**, **Proyectos**, **Mercado** y **Cuenta** ([ADR 0015](./decisiones/0015-taller-de-sistemas.md)): el objeto principal es el sistema de gobernanza (archivos, origen, ciclo y salida); uxyn propone cambios y tú decides.

## Tu cuenta: biblioteca, Taller y reportes

Con una cuenta en la web (Mercado, biblioteca, Taller/Creador y ventas), conecta el kit una vez por equipo y todo lo demás va solo:

| Quiero… | Comando |
|---|---|
| Conectar este equipo con mi cuenta | `uxyngraphar iniciar-sesion` (apruebas el código en la web) |
| Traer mi biblioteca (lo obtenido, comprado y mío) y ver qué proyectos pueden actualizarse | `uxyngraphar sincronizar` |
| Trabajar un borrador del Taller web en mi equipo | `uxyngraphar creador bajar <borrador>` y, al terminar, `uxyngraphar creador subir <id>` (también desde la barra de salida del Taller en el panel) |
| Contar al autor qué falla o falta | `uxyngraphar reportar <[editor/]id> --tipo problema\|mejora\|duda --texto "…"` (enseña antes lo que envía) |
| Desconectar este equipo | `uxyngraphar cerrar-sesion` |

Para publicar desde CI, usa una llave de automatización (se crea en la web) en la variable `UXYNGRAPHAR_TOKEN`. Las decisiones: [sesión por dispositivo](./decisiones/0011-sesion-por-dispositivo.md), [biblioteca sincronizada](./decisiones/0012-biblioteca-sincronizada.md), [Creador local e IA](./decisiones/0013-creador-local-e-ia.md) y [Taller de sistemas](./decisiones/0015-taller-de-sistemas.md).

## Actualizar, reparar, volver atrás y desinstalar

Las actualizaciones nunca dejan la herramienta rota: cada versión se descarga, se verifica (huella del sistema y de cada archivo) y se prueba **antes** de activarse; los datos (lista de proyectos, flujos guardados) se respaldan antes de cada cambio y, si algo falla, todo vuelve a como estaba. Los cambios en tus proyectos (instalar, actualizar, quitar sistemas) también se respaldan y se deshacen solos si fallan a mitad.

| Quiero… | Comando (o el botón equivalente en el panel, «Herramienta y ajustes») |
|---|---|
| Actualizar a la última | `uxyngraphar autoactualizar` (o vuelve a ejecutar la línea de instalación) |
| Volver a la versión anterior | `uxyngraphar usar anterior` |
| Arreglar algo que no va | `uxyngraphar reparar` (añade `--proyectos` para revisar también tus proyectos) |
| Si ni siquiera arranca | la línea de instalación con `--reparar` al final: `… \| python3 - --reparar` |
| Quitar un proyecto del panel | En **Proyectos**, «Quitar…»: **Solo desvincular** (sale de la lista y de sus grupos; la carpeta no se toca) o **Quitar todo** (además retira lo que puso uxyngraphar). Antes enseña la lista exacta de archivos y sistemas y pide una segunda confirmación; lo que modificaste se copia a `respaldos/quitados/` y lo que no creó uxyngraphar se queda. CLI: `uxyngraphar proyectos quitar RUTA [--todo] [--si]` |
| Desinstalar | `uxyngraphar desinstalar`: pregunta qué quitar (todo, solo la herramienta, uxyngraphar de tus proyectos o solo los accesos directos), enseña la lista exacta y pide confirmación |

Los sistemas que escribes (`crear`, el Taller) se guardan en `~/.uxyngraphar/catalogo/`, fuera de las versiones: reparar, actualizar, volver atrás o podar versiones antiguas no los tocan (los que crearon versiones anteriores dentro de `versiones/` se mueven ahí solos). Desinstalar la herramienta los lista y no los borra salvo que lo confirmes (`--con-catalogo`; en el panel, la casilla).

En el panel, **Mis sistemas** los ordena en carpetas (arrastrando o con «Mover a…»; solo es una vista, no mueve nada en el disco) y trae las herramientas de cada uno: abrir en el Taller, instalar, descargar, duplicar, cambiar el nombre y eliminar. Eliminar los lleva a una papelera recuperable (`uxyngraphar papelera`, `uxyngraphar restaurar <id>`); también hay `uxyngraphar eliminar`, `duplicar`, `renombrar` y `mis-sistemas`. Nada de esto toca el servidor ni lo publicado.

Los sistemas que ya no trabajas se pueden **archivar** (menú «…» en el Taller o en Mis sistemas, o `uxyngraphar archivar <id>` / `desarchivar <id>`): dejan de salir en el Taller sin borrar nada; siguen en tu catálogo, en tus proyectos y en la web, y «Mostrar archivados» o «Volver al Taller» los traen de vuelta. Un borrador que solo está en la web se «olvida» solo en este equipo.

En el Taller, los archivos de cada sistema se ven como en un editor de código: árbol con carpetas (crear, renombrar, mover y borrar), pestañas, resaltado de Markdown, JSON, Python, YAML y shell, números de línea, buscar y reemplazar (Ctrl+F / Ctrl+H), Ctrl+S, aviso de cambios sin guardar, vista previa de Markdown, «Ampliar» para usar toda la ventana y los errores de validación por archivo y línea. Las sugerencias de uxyn («Por revisar») se abren como diferencias en el editor y nunca bloquean: se aceptan, corrigen o descartan una a una o todas a la vez, y si un archivo cambió después de la sugerencia se elige entre aceptarla igualmente, aceptar solo lo que no choca o descartarla.

Al desinstalar, el trabajo de cada proyecto (`uxyngraphar/trabajo/`) se conserva salvo que pidas borrarlo (`--con-trabajo`). Sin terminal: `uxyngraphar desinstalar --alcance todo|herramienta|proyectos|accesos [--proyectos RUTA,RUTA] [--con-trabajo] [--con-catalogo] [--simular] --si`.

## Para quien contribuye

- [`CONTRIBUTING.md`](./CONTRIBUTING.md): pruebas, estilo, versiones y cómo se publica.
- [`español/motor/ARQUITECTURA.md`](./español/motor/ARQUITECTURA.md): módulos del motor y ciclo de vida de una transacción.
- [`español/motor/SOLUCION-DE-PROBLEMAS.md`](./español/motor/SOLUCION-DE-PROBLEMAS.md): certificados, proxy, Windows, candados, `reparar`, `deshacer` y `diagnostico`.
- [`decisiones/`](./decisiones/README.md): las decisiones de diseño del kit (ADR).

## Licencia

Copyright © 2026 uxleleaac / uxlelmar

Este kit se publica bajo **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**.

- Texto legal: [`LICENSE`](./LICENSE)
- Resumen: [`LICENCIA.md`](./LICENCIA.md)
- Detalle: [`LICENSING.md`](./LICENSING.md)
- Seguridad: [`SECURITY.md`](./SECURITY.md)

El **código** de la aplicación (API y UI) está en otros repositorios bajo **GPL-3.0** (con licencia comercial opcional). Ver `LICENSING.md`.
