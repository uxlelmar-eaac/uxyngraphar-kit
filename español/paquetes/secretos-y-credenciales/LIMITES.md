# Límites

Se cumplen en toda la tarea, en código, configuración, pruebas, documentación, fichas, commits y en la conversación.

1. **Solo placeholders.** En código, configuración, pruebas y documentación los valores sensibles se escriben como `<PLACEHOLDER>` o se leen de variables de entorno. Nunca un valor real, ni siquiera «temporal».
2. **No leas ni crees archivos de secretos.** Nada de abrir, imprimir, copiar o generar `.env`, `*.pem`, `*.key`, `id_rsa*`, `credentials.json`, `*.tfstate`, `.npmrc` con tokens, etc. Se permiten las plantillas sin valores (`.env.example`, `*.sample`, `*.template`).
3. **Nunca muestres un secreto completo.** Si necesitas referirte a uno, enmascáralo (primeros 4 caracteres + longitud).
4. **Escanea antes de cerrar.** `scripts/secretos.py` debe salir con código 0 sobre lo que tocaste.
5. **No silencies el escáner.** No añadas exclusiones a `ajustes.json`, ni la marca `uxyngraphar:permitir-secreto`, salvo en datos de prueba ficticios y con permiso de la persona.
6. **Un secreto real expuesto es un incidente.** No basta con borrarlo: avisa a la persona para que lo rote (guía `referencia/si-aparece-un-secreto.md`).
7. **Datos de prueba**: usa valores evidentemente falsos (`example`, `dummy`, `changeme`) o la marca `uxyngraphar:permitir-secreto` en la línea.
8. **Solo lo propio.** Un hallazgo en un archivo que no tocaste se avisa a la persona; no se borra, no se mueve y no se reescribe el historial.

## Cuándo detenerse y preguntar

- `secretos.py` encuentra un valor que parece real (no un placeholder ni un dato de prueba): detén la tarea y aplica `atender-incidente`.
- El pedido exige leer o crear un archivo de secretos (por ejemplo, «configura el `.env`»): explica cómo hacerlo con `.env.example` y que los valores los pone la persona.
- Un hallazgo es un falso positivo que solo se resuelve con `permitir` o con la marca: pide permiso antes.
- El secreto ya está en el historial de git o en un remoto.
