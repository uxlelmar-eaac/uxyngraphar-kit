# Solución de problemas

Lo primero, casi siempre: `uxyngraphar diagnostico` (añade `--anonimizar` si lo vas a pegar en una incidencia) y `uxyngraphar reparar --proyectos`.

## Instalar

- **macOS: «Python no puede verificar los certificados HTTPS».** Ejecuta «Install Certificates.command» (carpeta Aplicaciones > Python 3.x) y repite la línea de instalación. Si tienes `curl`, el instalador lo intenta también por su cuenta.
- **Detrás de un proxy.** Exporta `HTTPS_PROXY` (y `HTTP_PROXY`) antes de la línea de instalación; Python y `curl` los respetan.
- **Windows: `py` no existe.** Usa `python` en su lugar, o instala Python desde python.org marcando «py launcher». La línea `irm … | py -` no ejecuta ningún script de PowerShell, así que la política de ejecución no la bloquea.
- **Windows: el comando `uxyngraphar` no se encuentra.** Abre una terminal nueva (el PATH se lee al abrirla) o, desde el panel, «Herramienta y ajustes» > añadir el comando al PATH.
- **«Hay otra instalación de uxyngraphar en curso».** Espera a que termine. Si no hay ninguna, el candado se considera abandonado a los 15 minutos; también puedes borrar el archivo `.instalando` que indica el mensaje.
- **Aviso de procedencia.** Sin la CLI de GitHub (`gh`) con sesión, el instalador solo comprueba la huella SHA256 y lo dice. Para comprobar también la procedencia, ver [`SECURITY.md`](../../SECURITY.md).

## Proyectos

- **«Hay otro cambio en curso en este proyecto».** Otro proceso (el panel u otra terminal) está cambiándolo. Espera; si el proceso murió, el candado se retira solo en el siguiente intento.
- **«.claude/settings.json no es JSON válido (línea N)».** Ese archivo es tuyo y uxyngraphar no lo toca: corrige la línea (comas de más, comentarios) o bórralo.
- **Un sistema «ALTERADO».** Alguien cambió un archivo del sistema instalado. `uxyngraphar reparar --proyectos` lo reconstruye si el catálogo tiene su misma versión; si no, `actualizar`.
- **Algo salió mal tras instalar o actualizar.** `uxyngraphar deshacer --repo RUTA` (o «Deshacer…» en el panel) vuelve a antes del último cambio.
- **Fichas con status antiguos.** `uxyngraphar nomenclatura migrar --repo RUTA` (simula) y `--aplicar`.
- **Una verificación se cuelga.** Cada una tiene un límite (300 s por defecto, `verificar --segundos N`); si se agota, sale con código 124.

## Panel

- **«Este enlace ya se usó o caducó».** Cada enlace del panel vale una vez y durante 60 s. Ábrelo de nuevo con `uxyngraphar` o con su acceso directo.
- **El panel no abre.** `uxyngraphar panel --primer-plano` lo arranca atado a la terminal, con su registro a la vista; los errores también quedan en `panel.log` y `registros/panel.log` de la carpeta de uxyngraphar.
- **Un error interno en el panel.** El mensaje dice dónde está el registro con los detalles (`registros/panel.log`).

## La herramienta

- **No arranca.** La línea de instalación con `--reparar` al final la rehace sin tocar tus proyectos.
- **Quiero volver a la versión anterior.** `uxyngraphar usar anterior`.
