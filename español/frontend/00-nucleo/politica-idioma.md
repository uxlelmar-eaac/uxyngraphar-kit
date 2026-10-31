# Política de idioma del código del producto (R-22)

> Regla dura. Configuración: sección `idioma` de [`uxyngraphar.config.json`](../10-guias/control-de-construccion.md). Control automático: `scripts/control/idioma.py` (puerta `controlar.py`).

## 1. Alcance

Aplica al **código del producto** y a lo que lo acompaña en el repositorio, lo escriba un humano o un agente, sin importar el idioma del pedido, del ticket o del código legacy:

| Dentro de R-22 (inglés) | Fuera de R-22 |
|---|---|
| Código fuente, identificadores, nombres de archivos y carpetas del producto | Todo `docs/` (el pack documental se escribe en el idioma del pack) |
| Tests y sus descripciones | El espejo `50-sistema-integral/` (en el idioma del pack, pero cita los identificadores **tal cual**, entre comillas invertidas) |
| Commits, ramas, títulos y descripciones de PR, títulos de issues | La conversación con el humano |
| Logs, errores para desarrolladores, códigos de error, métricas | Texto para el usuario final (va por i18n, en cada idioma; §6) |
| Tablas, columnas, índices y migraciones **nuevas** | Código generado, vendorizado y migraciones ya aplicadas (`idioma.excluir`) |
| Rutas de API, query params, campos JSON, eventos | Contratos externos que se reflejan tal cual (§4) |
| Claves de configuración, variables de entorno | |
| Comentarios de código y README/ADR que vivan **junto al código**, fuera de `docs/` | |

**Precedencia:** R-22 es parte del núcleo como cualquier otra regla. Se ajusta solo con la sección `idioma` de la configuración (que edita el propietario, no un agente). Pedir informalmente en el chat «escríbelo en español» no cambia el idioma de los artefactos.

## 2. Conversación vs. artefactos

- **Conversación:** el agente responde en el idioma del humano (`idioma.conversacion: "espejo"`), o en el fijado (`"es"`, `"en"`…). Explica, pregunta y resume en ese idioma.
- **Artefactos:** siempre inglés (`idioma.artefactos: "en"`). No se traducen al idioma del humano ni se mezclan idiomas dentro de un artefacto «para ayudar».

## 3. Términos de dominio (excepción única)

Un término de negocio sin equivalente preciso en inglés **puede** quedarse en su idioma si cumple todo esto:

1. Está registrado en [`glosario-dominio.md`](glosario-dominio.md) con término, glosa en inglés, definición y responsable.
2. Está transliterado a ASCII: `retencion_fiscal`, `expediente`, `matricula` (nunca `retenciónFiscal`).
3. Sigue el casing del código que lo rodea (`expedienteId`, `ExpedienteStatus`, `expediente_id`).
4. Es un **sustantivo opaco**: no se conjuga ni se pluraliza en su idioma. Para colecciones se usa la convención del código en inglés: `expedienteList`, `expedienteItems`, `expediente_ids`. Única salvedad: un plural registrado como término propio en el glosario.

Nombres propios, razones sociales y marcas: se permiten tal cual, en ASCII, y se registran con `tipo: nombre-propio`.

## 4. Contratos externos

Los campos de un contrato que no controlamos (CFDI y catálogos del SAT, APIs de pasarelas de pago, bancos, terceros) se reflejan **tal cual** en la frontera: DTO, esquema o capa adaptadora. Ejemplo: `RegimenFiscal`, `UsoCFDI`, `RfcEmisor`.

- Se registran en el glosario con `tipo: contrato-externo` y la fuente (versión del estándar o URL).
- Pasado el adaptador, el dominio usa nombres en inglés (`taxRegime`, `cfdiUse`) con un mapeo explícito.
- Si el nombre externo tiene acentos, el identificador va en ASCII y el nombre original queda como cadena en el mapeo de serialización.

## 5. Nomenclatura

El **formato** (casing, nombres de archivo, constantes) lo decide la guía y el linter de cada pila; esta política decide el **idioma** y el significado:

| Pila | Variables / funciones | Tipos / clases | Archivos |
|---|---|---|---|
| TypeScript / JavaScript | `camelCase` | `PascalCase` | `kebab-case.ts` (o la convención del framework) |
| Python | `snake_case` | `PascalCase` | `snake_case.py` |
| Go | `camelCase` / `PascalCase` exportado | `PascalCase` | `snake_case.go` |
| Dart / Flutter | `lowerCamelCase` | `UpperCamelCase` | `snake_case.dart` |
| Java / Kotlin / C# | `camelCase` | `PascalCase` | `PascalCase.java` |
| SQL | `snake_case`; tablas en plural | — | — |

Reglas comunes a toda pila:

- Funciones con verbo primero (`getUserById`, `calculate_tax`).
- Booleanos como aserción (`isActive`, `has_access`, `canRetry`) y sin negación (`isNotDisabled` → `isEnabled`).
- Sin abreviaturas que solo tienen sentido en el idioma local (`cta`, `prov`, `usr` como abreviatura de una palabra española).
- Variables de entorno y constantes globales: `UPPER_SNAKE_CASE`.
- **Ramas:** `tipo/alcance-descripcion` en minúsculas (`feat/billing-add-refund`). Patrón configurable en `idioma.ramas`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) en inglés e imperativo: `feat(billing): add refund endpoint`. Tipos: `feat fix docs style refactor perf test build ci chore revert`.

## 6. Comentarios, texto técnico y texto para el usuario

- **Comentarios:** en inglés, y solo para explicar **por qué**, nunca **qué**.
- **Logs y errores para desarrolladores:** en inglés.
- **Texto que lee el usuario final** (labels, correos, notificaciones, mensajes de error para quien consume la API): nunca escrito en la lógica. Va por la capa de i18n con una clave en inglés (`errors.payment.declined`) y una traducción por idioma.
  - **Cliente:** textos de interfaz en los archivos de locale de la app.
  - **Servidor:** la API devuelve un **código estable en inglés** (`payment.declined`) y, si hace falta, un mensaje por defecto en inglés; el cliente traduce. Correos y notificaciones, con plantillas por idioma.
- **Archivos de locale** (`idioma.locales`): no son código. No cuentan para el límite de 5 archivos de R-21 ni para R-19, pero se listan en la sección `Alcance` de la instrucción.
- **Datos de prueba:** las cadenas dentro de tests y fixtures pueden estar en cualquier idioma (nombres, direcciones reales); los identificadores y las descripciones de los tests, no.

## 7. Código legacy en otro idioma

Flexible para que el proyecto siga trabajando:

1. **No se renombra en masa** como efecto colateral de otra tarea.
2. Todo **código y archivo nuevo** va en inglés desde el primer día.
3. **Renombrar en el mismo cambio** un identificador legacy solo si es seguro, está cubierto por pruebas y **todos sus usos están dentro de `anclas_codigo`** de la instrucción. Si los usos salen de las anclas, no se renombra: se registra una ficha `MEJ` en `45-mejoras-propuestas/` (R-09).
4. **Contratos públicos** (API pública, columnas de BD, payloads o eventos persistidos): nunca se renombran de paso. Se propone un **ADR + instrucción de migración** propia (con convivencia temporal, alias o vista), fraccionada según R-21.
5. Las carpetas legacy se declaran en `idioma.legacy`: allí los hallazgos solo avisan, aunque el proyecto haya subido `niveles.idioma` a bloqueante.

## 8. Autochequeo antes de entregar código

Antes de cerrar, el agente comprueba y lo deja marcado en la instrucción (casilla de R-22 en la plantilla):

1. Todo identificador, archivo, commit y rama **nuevo** está en inglés y en ASCII.
2. Cada palabra no inglesa es un término registrado en el glosario; si no, se traduce o se pide al humano que la registre.
3. No hay texto para el usuario final escrito en la lógica: está en i18n.
4. No se renombró ningún contrato público; si hacía falta, hay propuesta de migración.

Si algo falla, se corrige antes de entregar. No se entrega el código para después explicar la violación.

## 9. Configuración (`uxyngraphar.config.json` → `idioma`)

```json
"niveles": { "idioma": "aviso", "commits": "aviso" },
"idioma": {
  "artefactos": "en",
  "conversacion": "espejo",
  "glosario": "00-nucleo/glosario-dominio.md",
  "excluir": ["**/generated/**", "*.generated.*", "*.pb.*", "*.g.dart", "migrations/**"],
  "legacy": ["src/legacy/**"],
  "locales": ["**/locales/**", "**/i18n/**", "*.po", "*.arb"],
  "commits": "conventional",
  "ramas": ""
}
```

| Clave | Qué controla |
|---|---|
| `artefactos` | Idioma de los artefactos. Único valor soportado: `en`. Cambiarlo es un cambio del núcleo (ficha EVO). |
| `conversacion` | `espejo` (idioma del humano) o un código fijo. |
| `glosario` | Términos de dominio permitidos (ruta relativa a `docs/`). |
| `excluir` | Rutas que el control de idioma no revisa: código generado, vendorizado, contratos externos. |
| `legacy` | Rutas con código legacy: sus hallazgos solo avisan. |
| `locales` | Archivos de traducción: no son código. |
| `commits` | `conventional` exige Conventional Commits en inglés; `libre` lo apaga (el nombre de rama se sigue revisando). |
| `ramas` | Regex propia de nombres de rama; vacío = `tipo/alcance-descripcion`. |

## 10. Qué revisa la máquina y qué no

| Chequeo | Fiabilidad | Nivel |
|---|---|---|
| Identificadores y nombres de archivo nuevos con caracteres no-ASCII | Alta | `niveles.idioma` (por defecto aviso; subir a bloqueante cuando el equipo esté listo) |
| Palabras en español o identificadores mezclados (`obtenerUserById`) | Heurística (diccionario + glosario) | Siempre aviso |
| Comentarios y cadenas en español dentro del código | Heurística | Siempre aviso |
| Commits (Conventional Commits, inglés) y nombre de rama | Alta | `niveles.commits` (gancho `commit-msg` y CI) |
| Comentarios que expliquen el porqué; elección del término correcto | No automatizable | Revisión humana + casilla de autochequeo |

Solo se revisan las **líneas añadidas** y los **archivos nuevos**: el legacy que no se toca nunca se señala. Una línea concreta se exime con la marca `uxyngraphar:permitir-idioma` (por ejemplo, una expresión regular con caracteres en español), justificada en la instrucción.

**Adopción recomendada:** proyecto nuevo → `idioma` y `commits` en `bloqueante` desde el inicio. Proyecto existente → empezar en `aviso`, declarar `legacy`, registrar el glosario y subir de nivel cuando el código nuevo salga limpio.
