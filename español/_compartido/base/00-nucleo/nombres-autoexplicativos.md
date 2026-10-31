# Nombres autoexplicativos (R-23)

> **En una frase:** nombra por intención, dominio y unidad; usa comentarios solo para el *porqué*; trata cada comentario que explique el *qué* como señal de renombrar.

## 1. Principio

Un nombre debe explicar por sí solo **qué representa**, **para qué existe** y **cómo se usa** dentro del dominio del problema. Si hace falta un comentario para explicar qué es una variable, función, clase o constante, **el nombre está incompleto**.

- Los comentarios se reservan para el **porqué**, no para el **qué**.
- El nombre es la **documentación primaria**; el comentario es la **excepción**.

Alcance: todo identificador nuevo o tocado del código del producto (variables, constantes, funciones, métodos, clases, tipos, módulos, archivos, tests), en cualquier lenguaje. Los nombres van en inglés y ASCII ([R-22](politica-idioma.md)); los ejemplos de esta guía también.

## 2. Reglas (cualquier lenguaje)

### 2.1 Nombrar por intención, no por implementación

| ❌ Evitar | ✅ Preferir |
|----------|------------|
| `let d = 86400;` | `const SECONDS_PER_DAY = 86400;` |
| `function calc(a, b)` | `function calculateTotalPrice(basePrice, taxRate)` |

### 2.2 Incluir unidad o contexto cuando aporte significado

- ✅ `timeoutMs`, `weightKg`, `maxRetries`, `userEmail`.
- ❌ Nombres vacíos de significado: `data`, `info`, `value`, `temp`, `flag`, `x`.

### 2.3 Usar el vocabulario del dominio

Si el negocio habla de «factura», «suscripción» o «paciente», el código usa esos términos, no términos técnicos genéricos. Un nombre técnicamente correcto pero ajeno al dominio suele necesitar comentarios.

Enlace con R-22: el término del dominio va **en inglés** (`invoice`, `subscription`, `patient`) salvo que esté registrado en [glosario-dominio.md](glosario-dominio.md); en ese caso se usa tal cual figura allí.

### 2.4 Diferenciar por rol

| Rol | Forma | Ejemplos |
|-----|-------|----------|
| Variables y constantes | Sustantivos o frases nominales | `invoiceTotal`, `SECONDS_PER_DAY` |
| Funciones y métodos | Verbos o frases verbales | `sendEmail`, `calculateTax` |
| Booleanos | Predicados | `isActive`, `hasPermission`, `canRetry` |

Sin prefijos de tipo: ❌ `strName`, `intCount` → ✅ `name`, `count`; el sistema de tipos y el contexto ya lo dicen.

### 2.5 Evitar abreviaturas no universales

- ❌ `usr`, `cfg`, `mgr`, `tmp`: obligan a interpretar.
- ✅ Solo las estándar en el dominio o en el lenguaje: `url`, `id`, `http`, `i` en un bucle muy corto.

### 2.6 Nombrar las constantes mágicas

Cualquier número o cadena literal con significado de negocio tiene nombre.

```js
// ❌
if (status === 3) { /* ... */ }

// ✅
if (status === ORDER_STATUS.SHIPPED) { /* ... */ }
```

### 2.7 Consistencia

- **Un concepto = un nombre** en todo el proyecto: no alternar `user` / `cliente` / `customer` para lo mismo.
- Respetar las convenciones del lenguaje: `snake_case`, `camelCase`, `PascalCase`, `MAYÚSCULAS` para constantes, según la guía de cada pila.

### 2.8 Prueba del comentario

Antes de escribir un comentario, pregunta si un nombre mejor lo haría innecesario.

| Comentario | Acción |
|------------|--------|
| `// seconds in a day` | Renombrar a `SECONDS_PER_DAY` |
| `// if the user is active` | Renombrar a `isUserActive` |
| `// Refunds only apply within 30 days due to legal policy` | **Conservar**: explica una regla de negocio no obvia (el porqué) |

(Los comentarios del código también van en inglés según R-22.)

## 3. Excepciones

Se admiten nombres cortos o genéricos solo en:

- Índices de bucles muy cortos (`i`, `j`).
- Convenciones matemáticas (`x`, `y`, `n`).
- Lambdas de una línea con contexto obvio (`items.map(item => item.price)`).
- Nombres impuestos por APIs externas (se conservan en la frontera, como los contratos externos de R-22).
- Variables locales de alcance mínimo, donde un nombre largo no aporta.

## 4. Cumplimiento

| Mecanismo | Cómo |
|-----------|------|
| Code review | Ítem en la checklist: **«¿El nombre elimina la necesidad de un comentario?»** ([sync-documentacion-pr.md](../10-guias/sync-documentacion-pr.md), [tarjeta-referencia-humana.md](../10-guias/tarjeta-referencia-humana.md)) |
| Linters | Usar los linters y reglas de nombres del lenguaje (p. ej. reglas de *naming convention* de ESLint, `pep8-naming`/Ruff, `golint`/`revive`); se configuran en el proyecto, no en el pack |
| Revisión | Rechazar nombres genéricos (`data`, `info`, `value`, `temp`, `flag`) fuera de las excepciones |
| Refactor | Cuando aparezca un comentario que explique qué hace una variable o función, renombrar en el mismo cambio si el identificador está en `anclas_codigo`; si no, ficha en `45-mejoras-propuestas/` (R-09) |
| Guía de estilo | Documentar las convenciones de la pila en la guía de estilo del proyecto (p. ej. `00-nucleo/restricciones.md` o una ADR) |

Autochequeo del agente antes de cerrar (casilla R-23 en criterios de aceptación de la instrucción):

1. Cada identificador nuevo o tocado dice qué es y para qué sirve sin leer su cuerpo ni un comentario.
2. Unidades y contexto en el nombre cuando aplican; sin nombres vacíos ni abreviaturas no universales.
3. Constantes mágicas con nombre; un concepto, un nombre.
4. Ningún comentario nuevo explica el *qué*; los que quedan explican el *porqué*.

Legacy: no renombrar en masa. Renombrar solo lo que la instrucción toca y cuyos usos están en `anclas_codigo`; contratos públicos → ADR + migración (igual que R-22).

No hay control automático bloqueante: la regla se verifica en la revisión humana y con los linters del proyecto.
