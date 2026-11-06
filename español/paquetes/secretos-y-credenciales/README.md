# Secretos y credenciales

Activado con «usa el paquete secretos-y-credenciales» / «sigue el protocolo secretos» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app.

1. Integridad: `python3 uxyngraphar/paquetes/secretos-y-credenciales/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo) y cúmplelas durante toda la tarea.
3. Antes de terminar (y antes de proponer un commit): `python3 uxyngraphar/paquetes/secretos-y-credenciales/scripts/escanear.py`.
   - `--git` escanea solo lo que git versiona o tiene preparado; `--informe` guarda el resultado en `uxyngraphar/trabajo/secretos-y-credenciales/informes/`.
   - Código 1 = hay hallazgos: corrige **tu** cambio (sustituye por `<PLACEHOLDER>` o variable de entorno). Si el hallazgo no es tuyo, avisa a la persona; no lo borres ni lo muevas.
4. Qué hacer si aparece un secreto real: `uxyngraphar/paquetes/secretos-y-credenciales/docs/si-aparece-un-secreto.md`.

Ajustes del proyecto (los edita una persona): `uxyngraphar/trabajo/secretos-y-credenciales/ajustes.json` con `raices`, `excluir`, `permitir` (globs de rutas exentas) y `max_kb`.

## Reglas

Este paquete es inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Solo placeholders.** En código, configuración, pruebas y documentación los valores sensibles se escriben como `<PLACEHOLDER>` o se leen de variables de entorno. Nunca un valor real, ni siquiera «temporal».
2. **No leas ni crees archivos de secretos.** Nada de abrir, imprimir, copiar o generar `.env`, `*.pem`, `*.key`, `id_rsa*`, `credentials.json`, `*.tfstate`, `.npmrc` con tokens, etc. Se permiten las plantillas sin valores (`.env.example`, `*.sample`, `*.template`).
3. **Nunca muestres un secreto completo.** Si necesitas referirte a uno, enmascáralo (primeros 4 caracteres + longitud).
4. **Escanea antes de cerrar.** `scripts/escanear.py` debe salir con código 0 sobre lo que tocaste.
5. **No silencies el escáner.** No añadas exclusiones a `ajustes.json`, ni la marca `uxyngraphar:permitir-secreto`, salvo en datos de prueba ficticios y con permiso de la persona.
6. **Un secreto real expuesto es un incidente.** No basta con borrarlo: avisa a la persona para que lo rote (guía `docs/si-aparece-un-secreto.md`).
7. **Datos de prueba**: usa valores evidentemente falsos (`example`, `dummy`, `changeme`) o la marca `uxyngraphar:permitir-secreto` en la línea.
