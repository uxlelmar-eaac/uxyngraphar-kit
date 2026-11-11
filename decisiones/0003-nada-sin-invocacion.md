# 0003 · Nada se ejecuta sin que alguien lo invoque

- **Estado:** aceptada
- **Fecha:** 2026-11-10

## Contexto

Un kit que instala ganchos de git y workflows que ejecutan sus scripts en cada commit y en cada push sorprende a quien clona el proyecto, consume minutos de CI y hace que un fallo del kit bloqueara el trabajo.

## Decisión

uxyngraphar no instala ganchos, workflows ni tareas programadas por su cuenta. Las verificaciones se ejecutan cuando alguien las pide: la persona (CLI o panel) o el agente siguiendo el bloque de `AGENTES.md`. La integración en CI y el gancho pre-commit existen, pero solo se añaden cuando la persona lo pide (`uxyngraphar integracion` o el panel), llevan una marca y `retirar` los quita. Lo que decide una persona (aprobar, publicar, ejecutar pruebas de humo) lo ejecuta una persona: un agente no puede acreditarse como tal.

## Consecuencias

- `verificar` tiene una salida JSON estable y códigos 0/1/2 para quien quiera integrarlo.
