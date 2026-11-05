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

- Funciones: verbo + objeto. Booleanos: `is`/`has`/`can`/`should`.
- Colecciones en plural; elementos en singular.
- Constantes de dominio en un objeto o enum con nombre.
- Abreviaturas solo si son universales (`id`, `url`, `http`).
- Comentarios para el porqué (una decisión, una restricción externa), nunca para traducir un mal nombre.
