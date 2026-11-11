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

El instalador llega **vacío**: los sistemas de gobernanza se guardan en el servidor de uxyngraphar y los traes cuando los necesitas, desde el panel (vista «Sistemas de gobernanza») o con `uxyngraphar buscar <texto>` e `uxyngraphar instalar <id>`. Lo que traes queda guardado en tu equipo y sigue funcionando sin red. Quien escribe sistemas los publica con `uxyngraphar publicar <id>` (necesita un token de publicación). Ver [ADR 0007](./decisiones/0007-sistemas-en-el-servidor.md).

El instalador te pregunta si quieres un acceso directo en el menú de inicio, el escritorio o la barra de tareas. Después, el único comando que necesitas es **`uxyngraphar`** (o ese acceso directo): abre el panel en tu navegador, desde donde gestionas todo sin comandos. Añades tus proyectos, instalas, actualizas o quitas sistemas, ves y cambias el flujo del asistente, guardas flujos para reutilizarlos en otros proyectos y actualizas uxyngraphar.

## Actualizar, reparar, volver atrás y desinstalar

Las actualizaciones nunca dejan la herramienta rota: cada versión se descarga, se verifica (huella del sistema y de cada archivo) y se prueba **antes** de activarse; los datos (lista de proyectos, flujos guardados) se respaldan antes de cada cambio y, si algo falla, todo vuelve a como estaba. Los cambios en tus proyectos (instalar, actualizar, quitar sistemas) también se respaldan y se deshacen solos si fallan a mitad.

| Quiero… | Comando (o el botón equivalente en el panel, «Herramienta y ajustes») |
|---|---|
| Actualizar a la última | `uxyngraphar autoactualizar` (o vuelve a ejecutar la línea de instalación) |
| Volver a la versión anterior | `uxyngraphar usar anterior` |
| Arreglar algo que no va | `uxyngraphar reparar` (añade `--proyectos` para revisar también tus proyectos) |
| Si ni siquiera arranca | la línea de instalación con `--reparar` al final: `… \| python3 - --reparar` |
| Desinstalar | `uxyngraphar desinstalar`: pregunta qué quitar (todo, solo la herramienta, uxyngraphar de tus proyectos o solo los accesos directos), enseña la lista exacta y pide confirmación |

Al desinstalar, el trabajo de cada proyecto (`uxyngraphar/trabajo/`) se conserva salvo que pidas borrarlo (`--con-trabajo`). Sin terminal: `uxyngraphar desinstalar --alcance todo|herramienta|proyectos|accesos [--proyectos RUTA,RUTA] [--con-trabajo] [--simular] --si`.

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
