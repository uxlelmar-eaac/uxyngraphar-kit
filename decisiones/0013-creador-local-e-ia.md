# 0013 · Creador local sincronizado con la web y proveedores de IA

- **Estado:** aceptada
- **Fecha:** 2026-11-11
- **Plan:** `PLAN-PLATAFORMA/` (raíz de uxyngraphar), fase 6

## Contexto

El Creador web guarda borradores de sistemas en el servidor y usa IA con la clave de cada persona (cifrada en el
servidor). Quien prefiere su editor y sus herramientas debe poder trabajar en local con el mismo borrador, y quien usa
un modelo local (Ollama, LM Studio) no puede usarlo desde el servidor.

## Decisión

1. **Borradores**: `uxyngraphar creador bajar <id>` escribe el borrador en una carpeta con `.uxyngraphar-borrador.json`
   (`id`, `revision`). `creador subir <carpeta>` envía los archivos con esa revisión; si el servidor tiene otra, responde
   conflicto y el kit muestra qué archivos difieren sin sobrescribir nada.
2. **Validación**: la del propio motor (`especificacion.py`). El servidor ejecuta el mismo motor para el Creador web, de
   modo que hay una sola fuente de verdad del protocolo.
3. **IA desde el kit**: `creador mejorar` envía la instrucción y los archivos a `POST /v1/me/ia/completar` (usa la clave
   guardada en la cuenta) o, con `--local MODELO`, a un servidor compatible con OpenAI en `http://127.0.0.1` / `localhost`
   (`UXYNGRAPHAR_IA_LOCAL`, por defecto `http://127.0.0.1:11434/v1`). La respuesta se convierte en una propuesta que
   solo se aplica con `--aplicar` o desde el panel.
4. Solo biblioteca estándar (ADR 0001).

## Consecuencias

- Las claves de IA nunca se guardan en el equipo; el modelo local no necesita clave.
- Las propuestas se muestran como diferencias por archivo antes de aplicarse, igual que en la web.
