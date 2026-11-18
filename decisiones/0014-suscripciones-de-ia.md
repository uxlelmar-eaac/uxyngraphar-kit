# 0014 · Suscripciones de IA: en tu equipo con la CLI oficial y en la web solo donde el proveedor lo permite

- **Estado:** aceptada
- **Fecha:** 2026-11-18
- **Relacionada:** 0013 (Creador local e IA)

## Contexto

Quien ya paga Claude Pro/Max, ChatGPT, SuperGrok, Google AI, Copilot o un plan de programación (Qwen, GLM, Kimi,
MiniMax) quiere usarlo en el Creador en vez de pagar además una clave de API. Los términos de cada proveedor
(revisados el 2026-11-18) son distintos:

| Suscripción | Qué dicen sus términos | Web (servidor) | Kit (tu equipo) |
|---|---|---|---|
| Claude Pro/Max | El inicio de sesión solo vale dentro de Claude Code y Claude.ai (feb 2026); terceros, como uso extra | No | `claude -p` (es Claude Code) · riesgo medio |
| ChatGPT Go/Plus/Pro | «Sign in with ChatGPT» en vista previa: abierto a proyectos locales; apps comerciales con aprobación | OAuth con `client_id` propio · riesgo medio | `codex exec` · riesgo bajo |
| SuperGrok / X Premium+ | OAuth de xAI para agentes; cuota no documentada | OAuth (código de dispositivo) con `client_id` propio · riesgo medio | — |
| Google AI Pro/Ultra | Prohibido desde software de terceros, aunque envuelva su CLI; suspenden cuentas | No | No |
| Copilot Pro/Pro+ | Acuerdo formal solo con OpenCode | No | `copilot -p` · riesgo medio |
| Qwen | El OAuth gratuito cerró el 2026-04-15; ahora Coding Plan con clave | Clave del plan | `qwen -p` · riesgo bajo |
| GLM, Kimi, MiniMax, Ollama Cloud | El plan da una clave para herramientas | Clave del plan | Vía la cuenta |

## Decisión

1. **Nunca hacerse pasar por otra aplicación.** Ni la web ni el kit reutilizan el `client_id` de Claude Code, Codex
   u otras, ni leen o copian los tokens que guardan sus CLI.
2. **En tu equipo** (`ia_local.SUSCRIPCIONES`): el kit ejecuta la CLI oficial instalada, en una carpeta temporal
   vacía, con la conversación por la entrada estándar y sin pedirle herramientas. La sesión sigue dentro de la CLI.
   El panel (Conexiones) muestra cada una con su aviso de términos y riesgo; el Creador las lista al final y nunca
   las elige solo.
3. **En la web**: OAuth solo si quien administra el servidor registró uxyngraphar con el proveedor
   (`AI_OAUTH_<ID>_CLIENT_ID`); con riesgo no bajo hay que marcar «Entiendo el riesgo» y queda en la auditoría. Los
   planes con clave se pegan como cualquier clave. OpenRouter se conecta en un clic con su PKCE público.
4. **Lo prohibido no se ofrece** (Google AI Pro/Ultra): se explica por qué y se ofrece la clave de API.
5. En cada aviso se recomienda la clave de API, que es lo que recomiendan los proveedores.

## Consecuencias

- Las suscripciones del kit dependen de que la CLI esté instalada y con sesión; si no, el error dice cómo iniciarla.
- Hay que revisar los términos con cada cambio de los proveedores: la fecha de revisión se muestra en la web y el panel.
