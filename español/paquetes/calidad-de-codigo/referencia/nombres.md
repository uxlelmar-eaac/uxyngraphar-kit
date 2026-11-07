# Nombres autoexplicativos

Un buen nombre responde sin comentarios: ¿qué es?, ¿para qué sirve?, ¿en qué unidad o dominio?

| Evitar | Preferir | Por qué |
|--------|----------|---------|
| `data` | `pendingOrders` | Dice qué contiene |
| `timeout` | `requestTimeoutMs` | Unidad explícita |
| `flag` | `isEmailVerified` | Booleano con pregunta |
| `handle()` | `submitPaymentForm()` | Verbo + objeto |
| `status === 3` | `status === ORDER_STATUS.SHIPPED` | Sin números mágicos |
| `utils.ts` | `date-formatting.ts` | Archivo con responsabilidad |

Reglas:

- Funciones: verbo + objeto. Booleanos: `is`/`has`/`can`/`should`, como aserción y sin negación (`isEnabled`, no `isNotDisabled`).
- Colecciones en plural; elementos en singular.
- Constantes de dominio en un objeto o enum con nombre; constantes y variables de entorno en `UPPER_SNAKE_CASE`.
- Abreviaturas solo si son universales (`id`, `url`, `http`).
- Nombres de archivo sin espacios.
- Comentarios para el porqué (una decisión, una restricción externa), nunca para traducir un mal nombre.

## Formato por lenguaje

| Lenguaje | Variables / funciones | Tipos | Archivos |
|----------|-----------------------|-------|----------|
| TypeScript / JavaScript | `camelCase` | `PascalCase` | `kebab-case.ts` (o la convención del framework) |
| Python | `snake_case` | `PascalCase` | `snake_case.py` |
| Go | `camelCase` / `PascalCase` exportado | `PascalCase` | `snake_case.go` |
| Java / Kotlin / C# | `camelCase` | `PascalCase` | `PascalCase.java` |
| SQL | `snake_case`, tablas en plural | — | — |
