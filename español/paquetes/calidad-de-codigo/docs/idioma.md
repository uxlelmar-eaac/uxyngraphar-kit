# Idioma del producto

## Conversación y artefactos

- **Conversación:** en el idioma de la persona. Explicar, preguntar y resumir en su idioma.
- **Artefactos:** siempre en inglés y ASCII, aunque el pedido, el ticket o el código antiguo estén en otro idioma. Pedir en el chat «escríbelo en español» no cambia el idioma del código.

| En inglés | Fuera de esta regla |
|-----------|---------------------|
| Código, identificadores, nombres de archivos y carpetas | La documentación de `uxyngraphar/` (va en el idioma del equipo; cita los identificadores tal cual, entre comillas invertidas) |
| Pruebas y sus descripciones | La conversación |
| Commits, ramas, títulos y descripciones de PR | Texto para el usuario final (va por i18n, en cada idioma) |
| Logs, errores para desarrolladores, códigos de error | Código generado, vendorizado y migraciones ya aplicadas |
| Tablas, columnas y migraciones **nuevas** | Contratos externos reflejados tal cual (abajo) |
| Rutas de API, parámetros, campos JSON, eventos, variables de entorno | Cadenas de datos de prueba (nombres, direcciones reales) |
| Comentarios de código | |

## Términos del dominio

Un término de negocio sin equivalente preciso en inglés puede quedarse en su idioma **solo si** está en el glosario del proyecto (`uxyngraphar/trabajo/calidad-de-codigo/GLOSARIO.md`, lo mantiene la persona) y además:

1. Va en ASCII: `retencion_fiscal`, `expediente` (nunca `retenciónFiscal`).
2. Sigue el casing del código que lo rodea: `expedienteId`, `ExpedienteStatus`, `expediente_id`.
3. Es un sustantivo opaco: no se conjuga ni se pluraliza en su idioma (`expedienteList`, `expediente_ids`).

Si no está en el glosario, tradúcelo; si crees que debe estar, propónselo a la persona (no lo añadas tú).

## Contratos externos

Campos de contratos que no controlamos (facturación electrónica, pasarelas de pago, bancos) se reflejan tal cual **solo en la frontera** (DTO, esquema, adaptador) y se registran en el glosario con `tipo: contrato-externo` y su fuente. Pasado el adaptador, el dominio usa nombres en inglés con un mapeo explícito (`RegimenFiscal` → `taxRegime`).

## Texto para el usuario

Nunca escrito en la lógica: va por i18n con una clave en inglés (`errors.payment.declined`).

- **Cliente:** textos de interfaz en los archivos de locale.
- **Servidor:** la API devuelve un código estable en inglés (`payment.declined`) y, si acaso, un mensaje por defecto en inglés; el cliente traduce.

## Código antiguo en otro idioma

1. No se renombra en masa como efecto colateral de otra tarea.
2. Todo código y archivo **nuevo** va en inglés desde el primer día.
3. Se renombra en el mismo cambio solo si es seguro, hay pruebas y todos sus usos están dentro de las anclas de la tarea; si no, se registra como mejora.
4. Contratos públicos (API, columnas, eventos persistidos) nunca se renombran de paso: ADR + instrucción de migración con convivencia temporal.

## Formato por lenguaje

| Lenguaje | Variables / funciones | Tipos | Archivos |
|----------|-----------------------|-------|----------|
| TypeScript / JavaScript | `camelCase` | `PascalCase` | `kebab-case.ts` (o la convención del framework) |
| Python | `snake_case` | `PascalCase` | `snake_case.py` |
| Go | `camelCase` / `PascalCase` exportado | `PascalCase` | `snake_case.go` |
| Java / Kotlin / C# | `camelCase` | `PascalCase` | `PascalCase.java` |
| SQL | `snake_case`, tablas en plural | — | — |

Funciones con verbo primero; booleanos como aserción y sin negación (`isEnabled`, no `isNotDisabled`); sin abreviaturas del idioma local (`cta`, `usr`); constantes y variables de entorno en `UPPER_SNAKE_CASE`.

Ramas: `tipo/descripcion-corta` (`feat/checkout-coupons`). Commits: ver la regla 4 en `README.md`.
