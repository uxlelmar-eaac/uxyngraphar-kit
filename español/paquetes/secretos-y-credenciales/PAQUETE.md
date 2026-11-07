# Secretos y credenciales

Impide que credenciales, llaves y archivos de secretos entren al código o a la documentación: el agente solo escribe placeholders o variables de entorno, no toca archivos de secretos y escanea por contenido y por nombre antes de cerrar, sin mostrar nunca un valor completo.

## Qué resuelve

Una clave «de prueba» pegada en un cliente HTTP, un `.env` que se cuela en un commit o un token copiado en una ficha bastan para que una credencial quede expuesta para siempre en el historial. Y cuando aparece, la reacción habitual (borrar la línea) no la invalida. Este paquete fija cómo se escriben los valores sensibles, prohíbe leer o crear archivos de secretos, detecta patrones conocidos (AWS, GitHub, Stripe, Slack, Google, JWT, llaves privadas, URL con credenciales, asignaciones de `password`/`token`) y define qué hacer ante un secreto real.

## Problemas que cubre

- `secretos-en-el-codigo`: valores reales de credenciales en código, configuración, pruebas o documentación.
- `archivos-de-secretos-versionados`: `.env`, `*.pem`, `credentials.json`, `*.tfstate` y similares dentro del repositorio.
- `secretos-expuestos-sin-rotar`: un secreto real que se borra sin avisar ni revocar.
- `escaneo-silenciado`: exclusiones o marcas añadidas para que el escaneo pase.

## Fuera de alcance

- Revocar o rotar la credencial en el proveedor y gestionar un almacén de secretos: no lo cubre el kit; lo hace la persona.
- Limpiar el historial de git de un remoto: no lo cubre el kit; es decisión de la persona y del equipo.
- Qué comandos puede ejecutar la IA sin instrucción nueva: `herramientas-autorizadas`.
- Auditorías de seguridad con alcance y hallazgos (dependencias, permisos, configuración): `auditorias-tecnicas`.
- Otras prohibiciones de seguridad propias del equipo comprobables con regex: `reglas-del-proyecto`.

## Cuándo usarlo

- En cualquier tarea que toque configuración, clientes de servicios externos, despliegue o pruebas con credenciales.
- Antes de proponer un commit.
- Cuando la persona sospecha que un secreto llegó al repositorio.

## Cuándo no usarlo

- Para decidir dónde guardar los secretos en producción (almacén, variables del proveedor): no es un paquete de infraestructura.
- Para revisar vulnerabilidades del código o de las dependencias.

## Entradas y salidas

- Entradas: los archivos bajo `raices` (o los que git versiona o tiene preparados, con `--git`) y los ajustes en `uxyngraphar/trabajo/secretos-y-credenciales/ajustes.json` (`excluir`, `permitir`, `max_kb`).
- Salidas: código con placeholders o variables de entorno documentadas en `.env.example`, el informe de `secretos.py` (`ruta:línea: tipo (muestra enmascarada)`) y, con `--informe`, un `informes/escaneo-<fecha>.md` en el trabajo del paquete.

## Paquetes complementarios

- `herramientas-autorizadas`: limita qué comandos ejecuta la IA, incluidos los que podrían leer secretos.
- `auditorias-tecnicas`: la auditoría formal cuando un incidente pide revisar más a fondo.
- `reglas-del-proyecto`: prohibiciones de seguridad propias del equipo (por ejemplo, URLs internas).
