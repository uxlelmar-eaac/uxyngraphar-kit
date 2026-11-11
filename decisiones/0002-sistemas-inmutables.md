# 0002 · Sistemas de gobernanza inmutables y de solo lectura en los proyectos

- **Estado:** aceptada
- **Fecha:** 2026-11-10

## Contexto

Los agentes de IA leen los sistemas de gobernanza para saber cómo trabajar. Si un agente pudiera cambiarlos, podría rebajar sus propias reglas, y nadie distinguiría el sistema publicado del alterado.

## Decisión

Un sistema instalado en `uxyngraphar/sistemas-de-gobernanza/<id>/` es una copia construida desde el catálogo, con `INTEGRIDAD.json` (huella de cada archivo) y permisos de solo lectura. Solo el motor lo instala, lo actualiza o lo repara. El trabajo de cada sistema vive aparte, en `uxyngraphar/trabajo/<id>/`, y nunca se toca al actualizar. Al activar un sistema, el agente comprueba su integridad y, si falla, se detiene y avisa.

## Consecuencias

- Adaptar un sistema a un proyecto se hace con sus `ajustes`, no editándolo; lo que un sistema no permite se propone como EVO.
- Cada cambio que deba llegar a los proyectos sube la versión del sistema.
- Las reglas deny de `.claude/settings.json` refuerzan la barrera, pero son pasivas: la garantía es la integridad.
