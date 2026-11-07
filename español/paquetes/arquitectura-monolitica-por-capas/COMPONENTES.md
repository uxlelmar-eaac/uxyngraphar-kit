# Componentes

Las piezas que define el paquete. Rutas por defecto; el proyecto las ajusta en `ajustes.json`.

## Módulo

Carpeta de negocio bajo `modulos` (por defecto `src/modules/<modulo>/`). Agrupa todo lo de un área funcional y se divide en capas. Su archivo raíz (por ejemplo `orders.module.ts`) registra el módulo en el framework y puede importar otros módulos.

## Capa

Subcarpeta de primer nivel de un módulo cuyo nombre está en el perfil. Cada capa declara qué otras capas puede importar. Un archivo fuera de una capa reconocida no se revisa por capas, pero sí por cruces de módulo.

## Perfil

Conjunto de capas y dependencias permitidas (`perfil` en ajustes; se definen en `perfiles`).

**Servidor:**

| Capa | Puede importar |
|------|----------------|
| `presentation` | `application`, `security`, `sanitization`, `contracts` |
| `security` | `application`, `domain`, `contracts` |
| `sanitization` | `contracts`, `domain` |
| `application` | `domain`, `infrastructure`, `integrations`, `contracts`, `security` |
| `domain` | ninguna |
| `infrastructure` | `domain`, `contracts` |
| `contracts` | `domain` |
| `integrations` | `contracts`, `domain` |

**Cliente:**

| Capa | Puede importar |
|------|----------------|
| `components` | `hooks`, `model`, `types`, `styles` |
| `hooks` | `api`, `reception`, `model`, `types`, `integrations` |
| `api` | `types`, `model` |
| `reception` | `types`, `model` |
| `integrations` | `api`, `types`, `model` |
| `model` | `types` |
| `types` | ninguna |
| `styles` | ninguna |

## Frontera de integración

La capa `integrations/` (el `cruce` del perfil): el único lugar desde el que un módulo llama a otro. Expone métodos de propósito claro y oculta cómo es el otro módulo por dentro.

## Código común

Rutas en `comun` (por defecto `src/common/`): configuración, logging, acceso a datos, UI base. Lo usan todos los módulos y no importa ninguno.

## Desviación aceptada

Una excepción concreta a una restricción, autorizada por una ADR y anotada en «Desviaciones aceptadas» de `uxyngraphar/trabajo/arquitectura-monolitica-por-capas/ARQUITECTURA.md`.

## Nivel

`aviso` (por defecto): las infracciones se listan sin fallar la verificación. `bloqueante`: cualquier infracción la hace fallar. Una persona sube el nivel cuando el código está limpio.
