# Secretos y credenciales — reglas

Este paquete es inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Solo placeholders.** En código, configuración, pruebas y documentación los valores sensibles se escriben como `<PLACEHOLDER>` o se leen de variables de entorno. Nunca un valor real, ni siquiera «temporal».
2. **No leas ni crees archivos de secretos.** Nada de abrir, imprimir, copiar o generar `.env`, `*.pem`, `*.key`, `id_rsa*`, `credentials.json`, `*.tfstate`, `.npmrc` con tokens, etc. Se permiten las plantillas sin valores (`.env.example`, `*.sample`, `*.template`).
3. **Nunca muestres un secreto completo.** Si necesitas referirte a uno, enmascáralo (primeros 4 caracteres + longitud).
4. **Escanea antes de cerrar.** `scripts/escanear.py` debe salir con código 0 sobre lo que tocaste.
5. **No silencies el escáner.** No añadas exclusiones a `ajustes.json`, ni la marca `uxyngraphar:permitir-secreto`, salvo en datos de prueba ficticios y con permiso de la persona.
6. **Un secreto real expuesto es un incidente.** No basta con borrarlo: avisa a la persona para que lo rote (guía `guias/si-aparece-un-secreto.md`).
7. **Datos de prueba**: usa valores evidentemente falsos (`example`, `dummy`, `changeme`) o la marca `uxyngraphar:permitir-secreto` en la línea.
