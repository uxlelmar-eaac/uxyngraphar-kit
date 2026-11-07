# Componentes

Las piezas que define el paquete. Rutas por defecto; el proyecto las ajusta en `ajustes.json`.

## Revisión

Una comprobación de solo lectura que contrasta una clase de documentación con el código. Cada una devuelve hallazgos; si el paquete que necesita no está instalado, devuelve una nota `info` y no falla.

| Revisión | Compara | Necesita |
|----------|---------|----------|
| `rutas` | rutas del código (Nest, Express, Fastify, FastAPI, Flask) ↔ fichas `ruta` | `rutas-de-api` |
| `paginas` | páginas `app/**/page.*` (App Router de Next) ↔ fichas `pagina` | `paginas-de-interfaz` |
| `anclas` | rutas citadas en secciones cuyo título contiene «ancla» y en los campos `campos_ancla` ↔ archivos | — |
| `decisiones` | ADR `aceptada` con `comprobacion_prohibido` (y `aplica_a`) ↔ código | `decisiones-de-arquitectura` |
| `manuales` | manuales `vigente`: `ultima_verificacion` frente a `dias_manual` y rutas citadas | `manuales-operativos` |
| `vinculos` | ids citados (`XXX-AAAAMMDD-slug`) en el trabajo ↔ fichas existentes | — |
| `humo` | comandos de `humo` en ajustes; solo con `--ejecutar` | — |

## Hallazgo

Una diferencia entre documentación y código: severidad, texto y evidencia (`archivo:línea` o ruta de la ficha). Se imprime como `[revisión] severidad: hallazgo — evidencia`.

## Severidad

De mayor a menor: `critica`, `alta`, `media`, `baja`, `info`. `alta`: algo documentado como activo no existe, una decisión se incumple o el humo falla. `media`: falta documentación o una referencia está rota. `baja`: verificación caducada. `info`: notas que no cuentan como hallazgo (paquete no instalado, humo sin ejecutar).

## Ruta normalizada

Forma común para comparar rutas del código con las de las fichas: los parámetros `:id`, `{id}` y `[id]` pasan a `{}`, se unen barras repetidas y se añade `prefijo_global` delante de las rutas del código.

## Prueba de humo

Un comando de `humo` (`nombre`, `comando`, `segundos`) que se ejecuta desde la raíz de la app con `--ejecutar`. Falla si sale con código distinto de 0 o pasa del tiempo. Debe apuntar a un entorno de prueba.

## Informe

El resultado guardado con `--informe`: una auditoría `AUD-<fecha>-vivas-<revisiones>` con status `activa`, `findings_count` y `severidad` si está instalado `auditorias-tecnicas`; si no, `INFORME-<fecha>-<revisiones>.md` en el trabajo del paquete. Ambos llevan método, tabla de hallazgos y notas.
