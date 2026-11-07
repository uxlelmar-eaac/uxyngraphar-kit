# Caso: mejorar el alta de usuario

## Pedido

«Usa el paquete evaluaciones-de-usabilidad: el alta de usuario tiene muchas quejas, mejórala.» No hay ajustes propios: heurísticas por defecto y propuesta obligatoria desde severidad 3.

## Recorrido

**definir-alcance.** No hay evaluaciones previas del alta. Se abre la ficha y se pasa a `en-curso`:

```
python3 $P/scripts/comun/fichas.py nueva evaluacion --slug alta-usuario --titulo "Alta de usuario"
…/trabajo/evaluaciones-de-usabilidad/pendientes/UXE-20261106-alta-usuario.md
python3 $P/scripts/comun/fichas.py estado UXE-20261106-alta-usuario en-curso
…/trabajo/evaluaciones-de-usabilidad/en-progreso/UXE-20261106-alta-usuario.md
```

Alcance: `/signup` y `/signup/confirmar`; excluye el inicio de sesión. Tarea del usuario: «crear una cuenta con correo y contraseña».

**evaluar.** Recorriendo la tarea con las heurísticas (también solo con teclado), se registran dos problemas con `registrar-problema`:

```
| 1 | H9   | 3 | El error del formulario no dice qué campo falla      | `src/signup/form.tsx:88`           | -                                            | |
| 2 | A11Y | 4 | El botón «Crear cuenta» no recibe foco con teclado   | paso 4 del alta, recorrido con Tab | Usar `<Button>` en lugar de `div` con onClick | |
```

La verificación avisa de que falta la propuesta de la fila 1 (severidad 3):

```
python3 $P/scripts/verificar-evaluaciones.py
error: en-progreso/UXE-20261106-alta-usuario.md: problema 1: severidad 3 sin propuesta
evaluaciones: 1 errores, 0 avisos
```

Un `#3b82f6` suelto en `src/signup/form.module.css:12` existe, pero no afecta a la tarea: va a «Notas» como posible revisión con `componentes-de-interfaz`.

**proponer.** Al pasar a `propuesta` sin métricas, la verificación lo detecta:

```
error: en-progreso/UXE-20261106-alta-usuario.md: problema 1: severidad 3 sin propuesta
error: en-progreso/UXE-20261106-alta-usuario.md: en «propuesta» sin métricas (al menos una con Antes, Objetivo y Fuente)
evaluaciones: 2 errores, 0 avisos
```

Se completa la fila 1 («Mensaje bajo el campo, anunciado con aria-live») y, con `medir-metrica`, dos métricas:

```
| Pasos del alta              | 7  | 4    |  | conteo manual desde /signup        |
| Puntuación de accesibilidad | 81 | ≥ 95 |  | Lighthouse móvil, mediana de 3     |
```

`verificar-evaluaciones.py` queda en `evaluaciones: 0 errores, 0 avisos`. El agente se detiene y resume: dos problemas (un 4 de accesibilidad y un 3 de errores). Si intentara aprobar él mismo:

```
python3 $P/scripts/comun/fichas.py estado UXE-20261106-alta-usuario aprobada
error: «aprobada» solo lo asigna una persona (usa --humano si eres tú)
```

La persona marca «sí» en las dos filas y ejecuta `fichas.py estado UXE-20261106-alta-usuario aprobada --humano`.

**implementar.** Se cambia el `div` por el `<Button>` existente y el mensaje de error pasa junto al campo con `aria-live="polite"`. Se fusionan dos pasos redundantes del formulario que la fila 1 proponía. Se repite el alta solo con teclado: se completa. «Implementación» lista `src/signup/form.tsx`. Ficha a `implementada`.

**medir-resultado.** Misma fuente que «Antes»: pasos del alta 4, accesibilidad 97. Ninguna regresión. `verificar.py` y `verificar-evaluaciones.py` sin errores; la persona valida con `--humano`.

## Resultado

- Ficha `UXE-20261106-alta-usuario` en `completadas/` con dos problemas aprobados e implementados y dos métricas antes/después.
- El color suelto queda en «Notas» como posible revisión de consistencia; no se tocó.
