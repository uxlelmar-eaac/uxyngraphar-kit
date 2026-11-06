# Nomenclatura de los paquetes

Norma **propia del kit uxyngraphar**: rige solo lo que pertenece al kit (ids, títulos, familia, prefijos y status de fichas, frases de activación, scripts y archivos de los paquetes del catálogo). No se aplica al código, las carpetas ni los nombres de los proyectos donde se instalan los paquetes; eso es cosa de paquetes como `calidad-de-codigo`.

- Vocabulario y excepciones: `motor/nomenclatura.json`.
- Comprobación: `motor/nomenclatura.py`. La ejecutan `uxyngraphar validar` (errores con prefijo `nomenclatura:`), `uxyngraphar crear` (rechaza nombres que no cumplen) y el panel.
- Pendientes heredados: `uxyngraphar nomenclatura`.

## 1. Id del paquete (= nombre de la carpeta)

```
<objeto>[-<enlace>]-<calificador>    objeto: sustantivo en plural (lo que se gobierna)
                                     enlace: de | del | y | e | entre | por | con
```

1. Español, minúsculas, ASCII, sin dígitos, unido por guiones; **de 2 a 5 palabras** y como máximo 40 caracteres.
2. **Empieza por el objeto gobernado**, nunca por un verbo (`revisar-…`, `verificar-…`) ni por el nombre del kit (`uxyn-…`).
3. No empieza ni termina con un enlace, y solo usa los enlaces de la lista (`para`, `en`, `la`… no).
4. **Sin abreviaturas** (`repositorios`, no `repos`; `interfaz`, no `ui`). Siglas permitidas: `api`, `ux`, `adr`, `ci`.
5. Sin marcas, productos ni personas. Describe **qué se gobierna**, no la herramienta.
6. Único en el catálogo y **no es prefijo de otro id** (`rutas` y `rutas-de-api` no conviven).

| Bien | Mal | Por qué |
|------|-----|---------|
| `contratos-entre-repositorios` | `contratos-entre-repos` | abreviatura |
| `secretos-y-credenciales` | `escanear-secretos` | empieza por un verbo |
| `paginas-de-aterrizaje-bento` | `landing-bento` | anglicismo sin necesidad |
| `calidad-de-codigo` | `calidad` | una sola palabra |
| `reglas-del-proyecto` | `reglas-para-el-proyecto` | enlace no permitido |

## 2. Título, descripción y familia

- **Título = id en lenguaje natural**: las mismas palabras, en el mismo orden, con tildes y mayúscula inicial (`rutas-de-api` → «Rutas de API»; `mapa-de-modulos` → «Mapa de módulos»). Sin paréntesis ni subtítulos: el matiz va en la descripción.
- Descripción: una frase sobre lo que el paquete garantiza, ≤ 300 caracteres.
- `familia` (campo del manifiesto, no parte del id): `proceso`, `codigo`, `arquitectura`, `documentacion`, `seguridad`, `producto` o `sistema`.
- El README empieza por `# <título>`.

## 3. Tipos de ficha y prefijos

- Tipo: **sustantivo singular** del objeto (`ruta`, `decision`, `regla`, `contrato`, `pagina`).
- Prefijo: **exactamente 3 letras mayúsculas, único en todo el catálogo**. Reservados: `FIC` (plantilla), `TMP`, `UXY`, `XXX`. `crear` propone uno libre a partir del id.
- Plantilla: `plantillas/<tipo>.md`; variantes: `plantillas/<tipo>-<variante>.md`.
- Id de ficha: `<PREFIJO>-<AAAAMMDD>-<slug>`.

## 4. Status (vocabulario)

Español, minúsculas, kebab-case, concordando en género con el tipo (`instruccion aprobada`, `contrato aprobado`). Una sola palabra por fase:

| Fase | Status | Carpeta habitual | No usar |
|------|--------|------------------|---------|
| recién creada | `propuesta/o` | `pendientes` | `pending`, `draft` |
| en evaluación | `en-evaluacion` | `en-progreso` | — |
| aprobada | `aprobada/o` | `en-progreso` | `approved` |
| en vigor | `activa/o` · `vigente` | — / `completadas` | `active`, `authorized` |
| terminada | `hecha/o` · `cerrada/o` | `completadas` | `done`, `completada` |
| sustituida | `reemplazada/o` | `archivadas` | `superseded` |
| fuera de uso | `retirada/o` | `archivadas` | `deprecated`, `obsoleta/o`, `revoked` |
| archivada | `archivada/o` | `archivadas` | `archived` |
| rechazada | `rechazada/o` | `canceladas` | `rejected`, `cancelled` |
| a borrar | `para-eliminar` | `para-eliminar` | — |

Complementarios con significado propio: `pendiente` (por decidir o por hacer), `en-curso` (trabajo en marcha), `planificada/o`, `publicada/o`, `implementada/o`, `validada/o`, `cancelada/o` (la retira quien la propuso), `promovida/o`.

Excepciones de dominio (declaradas en `nomenclatura.json`, no se amplían sin decisión de la persona): `aceptada` en ADR (estándar de la industria) y `borrador` en manuales y páginas de aterrizaje.

**Status heredados**: los paquetes que vienen del 1.x conservan algunos status (en inglés y sinónimos) para no romper el trabajo de los proyectos. Están declarados por paquete en `nomenclatura.json` → `status.heredados`. No dan error, se listan con `uxyngraphar nomenclatura` y se quitan de la lista cuando el paquete migra (si el paquete deja de usar uno declarado, `validar` exige quitarlo). Ningún paquete nuevo puede declararlos.

## 5. Frases de activación

1. La primera es el id; la segunda, el id con espacios (`rutas de api`).
2. Las demás: **al menos dos palabras**, o un término inequívoco de `frases_de_una_palabra` (`adr`, `runbook`, `endpoints`, `uxyngraphar`…).
3. **Ninguna frase se repite en dos paquetes ni está contenida en la de otro** («decisiones» dentro de «decisiones pendientes» → error).
4. Minúsculas ASCII, sin tildes ni signos.
5. Toda frase que el README cite en «usa el paquete …» o «sigue el protocolo …» está en `activacion`.

## 6. Scripts y archivos

| Qué | Nombre | Ejemplo |
|-----|--------|---------|
| Script principal | `<tema>.py`, con el tema como sustantivo (nunca un verbo) | `rutas.py`, `capas.py`, `secretos.py` |
| Verificador | `verificar-<tema>.py` | `verificar-capas.py` |
| Módulo auxiliar importable | `<tema>_<aspecto>.py` | `capas_datos.py`, `secretos_patrones.py` |
| Común | `scripts/comun/` (lo copia `!base`) | — |
| Documento único del trabajo | MAYÚSCULAS, sin `id` en el frontmatter | `ARQUITECTURA.md`, `GLOSARIO.md` |
| Guías y plantillas | `docs/<tema>.md`, `plantillas/<nombre>.md` en kebab-case o MAYÚSCULAS | `docs/restricciones.md` |

## 7. Ajustes y frontmatter

- Claves de `ajustes` y campos nuevos de frontmatter: español, `snake_case`, sin abreviaturas (`dias_sin_cambios`, `ultima_verificacion`).
- Los campos heredados del 1.x en inglés (`approved_at`, `findings_count`…) se mantienen por compatibilidad; no se crean campos nuevos en inglés.

## 8. Crear un paquete

```
python3 motor/uxyngraphar.py crear contratos-de-pago --titulo "Contratos de pago" --familia arquitectura
```

`crear` comprueba id, título y familia, copia `paquetes/!base`, deriva el tipo (`contrato`), propone un prefijo libre (`CON`), renombra la plantilla a `plantillas/contrato.md` y deja la activación con el id y el id con espacios. Después, `validar` comprueba el resto de reglas a medida que se edita el paquete.
