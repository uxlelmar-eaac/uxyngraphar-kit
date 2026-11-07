# Componentes

Las piezas que define el paquete. Todas viven como fichas en `uxyngraphar/trabajo/reglas-del-proyecto/`.

## Regla

Ficha `REG-…` en `reglas/` (plantilla `plantillas/regla.md`). Una convención o prohibición del equipo sobre su código, con `nivel`, `aplica_a` (globs), `resumen` y, opcionalmente, una comprobación. Status: `propuesta` (no obliga), `activa` y `retirada`; los dos últimos solo los pone una persona.

## Comprobación

Los campos `comprobacion_prohibido` (regex que no puede aparecer en ninguna línea de los archivos de `aplica_a`) y `comprobacion_obligatorio` (regex que debe aparecer en cada archivo). Las evalúan `reglas.py comprobar` y `verificar-reglas.py` sin IA. Una regla sin comprobación sigue obligando como instrucción.

## Nivel

`bloqueante`: un incumplimiento sin excepción hace fallar la verificación. `aviso`: se informa sin fallar.

## Excepción

Ficha `EXC-…` en `excepciones/` (plantilla `plantillas/excepcion.md`). Permite incumplir una regla concreta (`regla`) en unos archivos (`archivos`; vacío = todos) hasta una fecha (`hasta`; `null` = sin plazo). Status: `pendiente` (no excusa nada), `aprobada` y `rechazada`; los dos últimos solo los pone una persona, que firma en `aprobada_por`.
