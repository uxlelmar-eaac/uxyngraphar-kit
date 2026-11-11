# Nomenclatura de los sistemas

Norma **propia del kit uxyngraphar**: rige solo lo que pertenece al kit (ids, títulos, familia, prefijos y status de fichas, frases de activación, scripts y archivos de los sistemas del catálogo). No se aplica al código, las carpetas ni los nombres de los proyectos donde se instalan los sistemas; eso es cosa de sistemas como `calidad-de-codigo` o `idiomas-del-codigo`.

- Vocabulario y excepciones: `motor/nomenclatura.json`.
- Comprobación: `motor/nomenclatura.py`. La ejecutan `uxyngraphar validar` (errores con prefijo `nomenclatura:`), `uxyngraphar crear` (rechaza nombres que no cumplen) y el panel.
- Pendientes heredados: `uxyngraphar nomenclatura`.

## 1. Id del sistema (= nombre de la carpeta)

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
- Descripción: una frase sobre lo que el sistema garantiza, ≤ 300 caracteres.
- `familia` (campo del manifiesto, no parte del id): `proceso`, `codigo`, `arquitectura`, `documentacion`, `seguridad`, `producto` o `plataforma`.
- El README empieza por `# <título>`.

## 3. Tipos de ficha y prefijos

- Tipo: **sustantivo singular** del objeto (`ruta`, `decision`, `regla`, `contrato`, `pagina`).
- Prefijo: **exactamente 3 letras mayúsculas, único en todo el catálogo**. Reservados: `FIC` (plantilla), `MEM` (memorias del proyecto), `TMP`, `UXY`, `XXX`. `crear` propone uno libre a partir del id.
- Carpeta de un tipo: `memorias` está reservada (es donde viven las memorias del proyecto, `trabajo/<id>/memorias/`).
- Archivos del núcleo (`sistema.json`, `README.md`, `SISTEMA.md`, `MEMORIAS.md`, `LIMITES.md`, `PERMISOS.md`): sus nombres no se usan en `docs/` ni en `plantillas/`.
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

**Status heredados**: hoy ningún sistema del catálogo los tiene. La tabla de equivalencias (status en inglés y sinónimos) de cada sistema está en [`vocabulario.json`](vocabulario.json), y las fichas de un proyecto que los usen se pasan con `uxyngraphar nomenclatura migrar --repo <ruta>` (simula; `--aplicar` las reescribe y las cambia de carpeta si hace falta, con respaldo y vuelta atrás). El mecanismo sigue en `nomenclatura.json` → `status.heredados` para una transición futura: un status declarado ahí no da error, se lista con `uxyngraphar nomenclatura` y, si el sistema deja de usarlo, `validar` exige quitarlo. Ningún sistema nuevo puede declararlos. La revisión cubre los status de `estados` y de `status_validos`.

## 5. Frases de activación

1. La primera es el id; la segunda, el id con espacios (`rutas de api`).
2. Las demás: **al menos dos palabras**, o un término inequívoco de `frases_de_una_palabra` (`adr`, `runbook`, `endpoints`, `uxyngraphar`…).
3. **Ninguna frase se repite en dos sistemas ni está contenida en la de otro** («decisiones» dentro de «decisiones pendientes» → error).
4. Minúsculas ASCII, sin tildes ni signos.
5. Toda frase que el README cite en «usa el sistema …» o «sigue el protocolo …» está en `activacion`.

## 6. Scripts y archivos

| Qué | Nombre | Ejemplo |
|-----|--------|---------|
| Script principal | `<tema>.py`, con el tema como sustantivo (nunca un verbo) | `rutas.py`, `capas.py`, `secretos.py` |
| Verificador | `verificar-<tema>.py` | `verificar-capas.py` |
| Módulo auxiliar importable | `<tema>_<aspecto>.py` | `capas_datos.py`, `secretos_patrones.py` |
| Común | `scripts/comun/` (lo copia `_base`) | — |
| Documento único del trabajo | MAYÚSCULAS, sin `id` en el frontmatter | `ARQUITECTURA.md`, `GLOSARIO.md` |
| Guías y plantillas | `referencia/<tema>.md`, `plantillas/<nombre>.md` en kebab-case o MAYÚSCULAS | `referencia/restricciones.md` |
| Fase del proceso | `proceso/<fase>.md`; la fase es un verbo en infinitivo o un sustantivo de acción, kebab-case, sin números (el orden lo da «proceso» del manifiesto) | `proceso/diagnosticar.md`, `proceso/disenar-modulo.md` |
| Skill | `skills/<nombre>/SKILL.md`; el nombre es la acción en infinitivo + objeto, kebab-case | `skills/crear-modulo/`, `skills/revisar-imports/` |
| Variante de andamiaje | `andamiaje/<variante>/`; lo que crea, kebab-case; `__nombre__` en rutas; código con sufijo `.plantilla` | `andamiaje/modulo-servidor/presentation/__nombre__.controller.ts.plantilla` |
| Ejemplo | `ejemplos/<caso>.md`, kebab-case | `ejemplos/modulo-orders.md` |
| Prueba del sistema | `pruebas/test_<tema>.py` | `pruebas/test_capas.py` |
| Extensión libre | nombre de primer nivel kebab-case, no reservado, declarado en «extensiones» | `catalogos/` |

### Excepción de nombre en el propio kit

La carpeta del idioma, `español/`, no sigue la regla de nombres ASCII: lleva `ñ`. Es una excepción conocida, no un modelo. Se mantiene porque es una ruta publicada (enlaces del README, instalador y `working-directory` de CI) y cambiarla rompería instalaciones y enlaces sin una ventaja práctica confirmada. En la shell se cita como cualquier ruta; en URLs va codificada (`espa%C3%B1ol`).

La base de los sistemas es `sistemas-de-gobernanza/_base/`: se ordena la primera y el catálogo la ignora por empezar por `_` (una `!` dispararía la expansión del historial de bash dentro de comillas dobles).

## 6.1 Problemas del alcance

- Id del problema (`alcance.problemas[].id`): **lo que sale mal**, como sustantivo + calificador, kebab-case, sin verbos en imperativo (`modulos-acoplados`, `capas-mal-importadas`; no `acoplar-modulos`).
- Descripción: una frase que describe el síntoma, no la solución.
- Un id por problema; `SISTEMA.md` los cita entre comillas invertidas en «Problemas que cubre».

## 7. Ajustes y frontmatter

- Claves de `ajustes` y campos nuevos de frontmatter: español, `snake_case`, sin abreviaturas (`dias_sin_cambios`, `ultima_verificacion`).
- Los campos del frontmatter en inglés (`approved_at`, `findings_count`…) se mantienen por compatibilidad; no se crean campos nuevos en inglés.

## 8. Crear un sistema

```
python3 motor/uxyngraphar.py crear contratos-de-pago --titulo "Contratos de pago" --familia arquitectura --piezas proceso,plantillas,cambios
```

`crear` comprueba id, título y familia, copia el núcleo de `sistemas-de-gobernanza/_base` (`sistema.json`, `README.md`, `SISTEMA.md`, `MEMORIAS.md`, `LIMITES.md`, `PERMISOS.md`, `scripts/comun/`) y añade las piezas pedidas desde `sistemas-de-gobernanza/_base/piezas/` (por defecto `plantillas`, `pruebas` y `cambios`; `pruebas` trae una prueba que compila cada script propio y prueba su `--help`). Con `plantillas` deriva el tipo de ficha (`contrato`), propone un prefijo libre (`CON`) y renombra la plantilla a `plantillas/contrato.md`. La activación queda con el id y el id con espacios. El núcleo lleva marcadores `{{…}}`: el sistema no valida hasta rellenarlos. Las piezas se añaden o quitan después con `uxyngraphar pieza <id> agregar|quitar <pieza>`.
