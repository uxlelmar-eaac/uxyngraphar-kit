# 0011 · El kit se conecta a la cuenta con un flujo de dispositivo

- **Estado:** aceptada
- **Fecha:** 2026-11-11
- **Plan:** `PLAN-PLATAFORMA/` (raíz de uxyngraphar), fase 2

## Contexto

Publicar exigía crear un «espacio de publicador», generar un token en la web y pegarlo con `uxyngraphar sesion guardar`.
Las personas no entendían el proceso y el token viajaba por el portapapeles. Además, la biblioteca en la nube (sistemas
comprados y privados) necesita que el kit sepa quién es la persona, no solo con qué espacio publica.

## Decisión

1. `uxyngraphar iniciar-sesion` usa un **flujo de dispositivo** (RFC 8628 simplificado): pide un código al servidor
   (`POST /v1/dispositivo/codigo`), muestra el código corto, abre el navegador en `…/conectar?codigo=…` y consulta
   `POST /v1/dispositivo/token` cada pocos segundos hasta que la persona aprueba, deniega o caduca (10 minutos).
2. El servidor entrega un **token de sesión del kit** (`uxk_…`) ligado a la cuenta y al nombre del equipo. Se guarda en
   `~/.uxyngraphar/sesion.json` con permisos privados (como el token anterior) y viaja como `Authorization: Bearer`.
3. La sesión sirve para publicar en el `@usuario` de la persona, sincronizar la biblioteca (ADR 0012), los borradores
   y reportar al autor. Se revoca desde la web («Equipos conectados») o con `uxyngraphar cerrar-sesion`.
4. Los **tokens de publicación** (`uxp_…`, `sesion guardar`) siguen funcionando para automatizaciones (CI) y tienen
   prioridad si están en `UXYNGRAPHAR_TOKEN`.
5. Solo biblioteca estándar (ADR 0001): `urllib`, `json`, `webbrowser`.

## Consecuencias

- Nada sensible pasa por el portapapeles; el código corto no sirve sin la aprobación en una sesión web.
- Sin red, el kit sigue funcionando con la caché; los comandos que necesitan la cuenta lo dicen con claridad.
- Nada se ejecuta solo (ADR 0003): la sincronización ocurre al iniciar sesión, al abrir el panel o con `sincronizar`.
