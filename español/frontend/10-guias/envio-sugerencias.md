# Envío de sugerencias (opcional)

uxyngraphar es abierto: si quieres, las fichas de `46-evolucion-documentacion/` (fichas **EVO**: mejoras del propio sistema documental) llegan a quien lo mantiene para que las mejoras entren en el pack. **Colaborar es libre: está apagado hasta que una persona responde «Sí».**

## La pregunta al instalar o actualizar

Al instalar uxyngraphar (pantalla del navegador o consola), y la primera vez que actualizas un proyecto que todavía no la respondió, el asistente pregunta **una sola vez**:

> ¿Te gustaría colaborar en la mejora de uxyngraphar? · **Sí** · **No**

- Ninguna opción viene marcada. Antes de responder ves en lenguaje llano qué sale y qué no (la tabla de abajo).
- **Sí:** se activa el envío en `docs/uxyngraphar.config.json` (sección `feedback`) con el consentimiento, la fecha, la versión de los términos (`v1`), un identificador aleatorio de la instalación y el origen (`instalador` o `actualizador`).
- **No:** el envío queda apagado y se registra `respondido: "no"` con la fecha, para no volver a preguntar.
- En modo automático (`--si`) sin respuesta explícita cuenta como **No**; si lo ejecuta el CI o un agente (mismas variables que abajo), la pregunta **queda pendiente** para la persona: ni el CI ni el agente la contestan (R-25). Para responder sin pantalla: `--colaborar si` o `--colaborar no` (en `instalar.py`, `actualizar.py` y `uxyngraphar instalar|actualizar`).
- Puedes cambiar de opinión cuando quieras: `feedback.py activar` (Sí) o `feedback.py revocar` (No).

## Cuándo se envía

Con el envío activo, **al terminar cada `instalar` o `actualizar` que ejecuta una persona** se envían solas las fichas EVO nuevas o cambiadas desde el último envío, y ves una línea con cuántas salieron. Si no hay red, solo se avisa: la instalación o actualización no falla y lo pendiente sale la próxima vez (o con `feedback.py enviar`).

**Nunca** se envía desde CI, ganchos de git ni el agente: el envío automático no se ejecuta si detecta CI (`CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `BUILDKITE`, `JENKINS_URL`) o un agente (`CLAUDECODE`, `UXYNGRAPHAR_AGENTE`), y las reglas prohíben al agente activar o ejecutar el envío (R-25).

## ¿Es telemetría?

Es *feedback* (sugerencias que escriben personas y agentes), no métricas de uso. Se trata con las mismas garantías que la telemetría seria:

| Garantía | Cómo se cumple |
|----------|----------------|
| Opt-in | `feedback.activo` es `false` hasta que una persona responde **Sí** en el instalador o el actualizador, o ejecuta `feedback.py activar`. Ninguna opción viene marcada. |
| Consentimiento registrado | Fecha y versión de los términos en `uxyngraphar.config.json` → `feedback.consentimiento`, más `respondido`, `respondido_en` y `origen`. Activarlo a mano sin consentimiento hace la configuración inválida. |
| El agente no decide | El archivo de configuración está fuera del alcance del agente (reglas `deny`, R-20) y las reglas le prohíben activar o ejecutar el envío (R-25). |
| Nunca desde CI, ganchos ni el agente | Solo se envía al final de `instalar`/`actualizar` hechos por una persona o con `feedback.py enviar`. |
| Datos mínimos | Solo fichas EVO (tabla de abajo). Siempre puedes ver la copia exacta con `previsualizar`. |
| Revocable y borrable | `feedback.py revocar` apaga el envío; con `--borrar-remoto` pide además al receptor que borre lo recibido de tu instalación. |

## Qué sale y qué no

| Sale | No sale nunca |
|------|---------------|
| De cada EVO: id, estado, tipo, impacto, prioridad, archivos del pack que propone cambiar y su texto | Código, historia de git, ramas, remotos |
| Versión y tipo de pack (servidor/cliente) | Nombre de la carpeta del proyecto (`[proyecto]`) y los nombres que pongas en `feedback.ocultar` (`[oculto]`) |
| Un identificador aleatorio de la instalación (para pedir el borrado) | Rutas de tu equipo, correos, enlaces (se cambian por `[ruta]`, `[correo]`, `[enlace]`) |
| | Líneas que parezcan credenciales (se omiten), comentarios HTML, campo `areas` |
| | Usuario, nombre del equipo, ajustes locales (`97-ajustes-locales/`), métricas de uso |

Una ficha ya enviada no se vuelve a enviar salvo que cambie (`feedback_huella`).

Si tus fichas nombran a un cliente, un producto o tu empresa, añádelos: `"feedback": {"ocultar": ["Acme", "Tienda Acme"]}` en `docs/uxyngraphar.config.json`. Lo demás de la sección `feedback` no se toca a mano.

## Uso a mano

```bash
python3 docs/scripts/feedback.py previsualizar --salida copia.json   # mira exactamente qué saldría
python3 docs/scripts/feedback.py activar                             # usa el receptor oficial; --url para otro
python3 docs/scripts/feedback.py enviar
python3 docs/scripts/feedback.py estado
python3 docs/scripts/feedback.py revocar --borrar-remoto
```

Si el receptor pide token: variable de entorno `UXYNGRAPHAR_FEEDBACK_TOKEN` (nunca en el repo). Solo se aceptan direcciones `https://`; `http://` solo hacia `127.0.0.1`/`localhost` para pruebas.

Sin receptor: `python3 docs/scripts/exportar-evo.py --salida propuestas-evo.md --marcar` genera un informe para mandarlo a mano.

## Para quien mantiene uxyngraphar

El receptor oficial es el backend de uxyngraphar (NestJS + Postgres), repo `uxyngraphar-backend`: recibe en `POST /v1/sugerencias`, deduplica, borra por instalación (`DELETE /v1/instalaciones/<id>`) y muestra las fichas e informe en su panel ROOT. La dirección oficial está en una sola constante del kit (`URL_FEEDBACK_OFICIAL` en `scripts/feedback/cliente.py`). Al implementar una sugerencia en el pack, **cita su id EVO en el CHANGELOG**: los proyectos que la aplicaron en local verán con `ajustes.py verificar` que ya pueden retirar su ajuste.
