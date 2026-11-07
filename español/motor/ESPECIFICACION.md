# Especificación — paquetes de gobernanza uxyngraphar 2.0

Validadores: [`especificacion.py`](especificacion.py) (paquete y flujo), [`piezas.py`](piezas.py) (una función por pieza estándar) y [`paquetes/!base/scripts/comun/uxyn_base.py`](../paquetes/!base/scripts/comun/uxyn_base.py) (manifiesto e integridad; cada paquete lleva su propia copia en `scripts/comun/`).

## 1. Estructura en un repo

```
<raiz-app>/
  AGENTES.md · AGENTS.md          bloque generado entre <!-- uxyngraphar:inicio --> y <!-- uxyngraphar:fin -->
  uxyngraphar/                    todo uxyngraphar en una sola carpeta
    INDICE.md                     generado por el motor
    FLUJO.json                    lo edita solo una persona
    paquetes/<id>/                un paquete (inmutable; lo escribe solo el motor)
    trabajo/<id>/                 trabajo de cada paquete (editable)
      ajustes.json                opcional: sobrescribe «ajustes» del manifiesto
      <estado>/<ficha>.md         paquete con un solo tipo de ficha (p. ej. decisiones-de-arquitectura/completadas/ADR-…md)
      <tipo>/<estado>/<ficha>.md  tipo con carpeta propia (p. ej. instrucciones-aprobadas/instrucciones/pendientes/INS-…md)
```

Sin números delante de las carpetas ni carpetas por fecha: la fecha va en el id de la ficha.

Un paquete resuelve su trabajo como `<carpeta-del-paquete>/../../trabajo/<id>/`.

## 2. Paquete: el protocolo

La base (`paquetes/!base/`) es un **protocolo**, no un molde: fija cómo se organiza un paquete, no qué tiene que contener. Cada paquete es un monolito autosuficiente y especializado (un conjunto acotado de problemas o acciones): copiar su carpeta a otro `uxyngraphar/paquetes/` basta para usarlo, y cada pieza se agrega, mejora o quita sin tocar las demás. Tres niveles:

**Nivel 1. Núcleo obligatorio** (lo único que da errores si falta):

```
<id>/
  paquete.json                    manifiesto (§3): identidad, alcance, piezas y extensiones
  README.md                       entrada del agente: bloque generado entre <!-- uxyngraphar:entrada:inicio --> y
                                  <!-- uxyngraphar:entrada:fin --> a partir del manifiesto; el resto es libre del autor
  PAQUETE.md                      ficha de descripción (§2.1)
  scripts/comun/                  infraestructura común (nace de paquetes/!base): uxyn_base.py, uxyn_fichas.py, fichas.py,
                                  verificar.py, verificar-integridad.py, andamiar.py
  INTEGRIDAD.json                 solo en paquetes construidos/instalados (§4)
```

**Nivel 2. Piezas estándar** (opcionales; se declaran en «piezas»; si existen, siguen su forma — §2.2):

| Pieza | Ruta | Forma |
|-------|------|-------|
| `limites` | `LIMITES.md` | `# Límites`; reglas duras numeradas; opcional «## Cuándo detenerse y preguntar» |
| `proceso` | `proceso/<fase>.md` | una fase por archivo, en el orden de «proceso»; frontmatter `fase`, `resuelve`, `skills`; secciones «Objetivo», «Pasos», «Criterio de salida» (y «Entradas») |
| `skills` | `skills/<nombre>/SKILL.md` | frontmatter `name` (= carpeta), `description`, `resuelve`; secciones «Cuándo usarla», «Pasos» (y «Resultado»); la carpeta puede llevar más archivos |
| `componentes` | `COMPONENTES.md` | `# Componentes`; una sección `## <componente>` por pieza conceptual |
| `herramientas` | `HERRAMIENTAS.md` | `# Herramientas`; documenta cada script ejecutable de `scripts/` (aviso si falta alguno) |
| `andamiaje` | `andamiaje/<variante>/` | una carpeta por variante de «andamiaje»; `__nombre__` en rutas; `{{nombre}}`, `{{Nombre}}`, `{{nombreCamel}}` en el contenido |
| `plantillas` | `plantillas/` | plantillas de fichas (§3.1) y documentos que el paquete copia al trabajo |
| `referencia` | `referencia/` | guías de consulta (`.md`) |
| `ejemplos` | `ejemplos/` | casos resueltos de principio a fin (`.md`) |
| `pruebas` | `pruebas/test_*.py` | pruebas propias con `unittest`, ejecutables desde la carpeta del paquete sin el motor |
| `cambios` | `CHANGELOG.md` | `# Cambios`; una sección `## X.Y.Z` por versión (aviso si falta la actual) |

**Nivel 3. Extensiones libres:** carpetas o archivos de primer nivel propios del paquete, declarados en «extensiones» con una frase de para qué sirven. Solo cumplen las reglas de portabilidad.

Cualquier otra entrada de primer nivel es un error: o es una pieza estándar, o se declara como extensión. Los scripts propios del paquete van en `scripts/` (fuera de `scripts/comun/`).

### 2.1 `PAQUETE.md`

Empieza por `# <título>` y una o dos frases de lo que garantiza. Secciones obligatorias: «Qué resuelve», «Problemas que cubre» (cita cada id de `alcance.problemas` entre comillas invertidas), «Fuera de alcance», «Cuándo usarlo», «Entradas y salidas». Recomendadas: «Cuándo no usarlo», «Paquetes complementarios».

### 2.2 Errores y avisos

El validador separa lo que rompe el paquete de lo que solo orienta:

- **Errores:** falta un archivo del núcleo; marcadores `{{…}}` en el núcleo (`paquete.json`, `README.md`, `PAQUETE.md`); secciones obligatorias de `PAQUETE.md`; bloque de entrada del README desfasado (`uxyngraphar indice-paquete <id>` lo regenera); una pieza declarada que falta o no sigue su forma; una pieza presente sin declarar; una fase o skill citada que no existe; un `resuelve` que cita un problema inexistente; una extensión declarada que falta; una entrada de primer nivel no declarada; portabilidad.
- **Avisos:** más de 5 problemas (posible paquete generalista); un problema que no cubre ninguna fase ni skill; una skill sin `resuelve`; piezas recomendadas para la familia que faltan; marcadores en piezas opcionales; scripts sin documentar en `HERRAMIENTAS.md`; `scripts/comun/` distinto de `!base`.

`uxyngraphar validar --completitud` muestra, por paquete, las piezas presentes, las recomendadas que faltan y las extensiones.

### 2.3 Portabilidad

- Ningún script importa nada de fuera de la carpeta del paquete ni supone rutas fijas del repo.
- Ningún script escribe fuera de `uxyngraphar/trabajo/<id>/`, salvo el andamiaje (en el destino declarado, sin sobrescribir) o una ruta explícita de la persona.
- Nombres de archivo ASCII y sin espacios; Python solo con librería estándar.
- Copiar la carpeta a otro `uxyngraphar/paquetes/` produce el mismo comportamiento.

`paquetes/!base/` guarda el núcleo de partida y, en `piezas/<pieza>/`, la semilla de cada pieza estándar (sus archivos y, si la pieza añade campos al manifiesto, un `manifiesto.json` con ellos). No es un paquete: el catálogo lo ignora, no se construye ni se instala. `crear` copia el núcleo y las piezas pedidas; `pieza <id> agregar|quitar <pieza>` añade o retira una pieza después.

## 3. Manifiesto `paquete.json`

| Campo | Tipo | Regla |
|-------|------|-------|
| `manifiesto_formato` | entero | `2` |
| `id` | texto | kebab-case ASCII; igual al nombre de la carpeta; cumple `NOMENCLATURA.md` |
| `version` | texto | semver `X.Y.Z` |
| `titulo`, `descripcion` | texto | no vacíos; título = id en lenguaje natural (`NOMENCLATURA.md`) |
| `familia` | texto | `proceso`, `codigo`, `arquitectura`, `documentacion`, `seguridad`, `producto` o `sistema` |
| `motor` | texto | `>=X.Y`; versión mínima del motor |
| `activacion` | lista | frases que activan el paquete: el `id`, el id con espacios y otras sin repetir ni contener las de otro paquete |
| `entrada` | texto | `README.md` |
| `verificaciones` | lista | `scripts/*.py` que el agente ejecuta antes de cerrar (la genérica: `scripts/comun/verificar.py`) |
| `fichas` | objeto | opcional; tipos de ficha (§3.1) |
| `ajustes` | objeto | opcional; valores por defecto que el proyecto puede sobrescribir en `ajustes.json` |
| `protegidos` | lista | opcional; globs relativos a `trabajo/<id>/` que la IA no edita (reglas `deny` de Claude) |
| `fuera_de_ia` | lista | opcional; globs relativos a `trabajo/<id>/` que la IA no lee (`.cursorignore` y equivalentes) |
| `al_activar_paquete` | texto | opcional; `scripts/… {id}` que el agente ejecuta al activar cualquier paquete (`{id}`: el activado); p. ej. ajustes locales |
| `alcance` | objeto | `problemas`: lista no vacía de `{id, descripcion}` (ids kebab-case únicos); `fuera_de_alcance`: lista no vacía de `{tema, derivar_a}` (`derivar_a`: id de paquete o `null`) |
| `piezas` | lista | piezas estándar presentes (§2), sin repetir; puede estar vacía |
| `proceso` | lista | solo con la pieza `proceso`: fases en orden (kebab-case), una por `proceso/<fase>.md` |
| `andamiaje` | objeto | solo con la pieza `andamiaje`: `{variante: {descripcion, destino}}`; `destino` relativo a la raíz de la app, admite `{nombre}` |
| `extensiones` | objeto | opcional; `{ruta-de-primer-nivel: para qué sirve}` |

`fichas` exige la pieza `plantillas`.

### 3.1 Tipos de ficha

```json
"fichas": {
  "adr": {
    "carpeta": ".",
    "prefijo": "ADR",
    "plantilla": "plantillas/adr.md",
    "inicial": "propuesta",
    "estados": {"propuesta": "pendientes", "aceptada": "completadas", "rechazada": "canceladas"},
    "solo_humano": ["aceptada", "rechazada"]
  }
}
```

Con varios tipos, cada uno tiene su carpeta:

```json
"fichas": {
  "regla": {
    "carpeta": "reglas",
    "prefijo": "REG",
    "plantilla": "plantillas/regla.md",
    "inicial": "propuesta",
    "estados": {"propuesta": "propuestas", "activa": "activas", "retirada": "retiradas"},
    "solo_humano": ["activa", "retirada"]
  },
  "excepcion": {"carpeta": "excepciones", "prefijo": "EXC", "plantilla": "plantillas/excepcion.md", "inicial": "pendiente",
                "estados": {"pendiente": "pendientes", "aprobada": "aprobadas", "rechazada": "rechazadas"}}
}
```

Un tipo plano usa `status_validos` en lugar de `estados`:

```json
"ruta": {"carpeta": ".", "prefijo": "RUT", "plantilla": "plantillas/ruta.md", "inicial": "activa", "status_validos": ["activa", "deprecada"]}
```

- `carpeta`: `.` (raíz del trabajo del paquete; solo si hay un único tipo) o un nombre kebab-case.
- Con `estados`: la ficha vive en `uxyngraphar/trabajo/<id>/<carpeta>/<carpeta-de-estado>/<ficha>.md`; las carpetas de estado son kebab-case sin números (`pendientes`, `en-progreso`, `completadas`, `archivadas`, `canceladas`, `para-eliminar`) y el `status` debe corresponder a la carpeta.
- Con `status_validos` (plana): vive en cualquier subruta de `<carpeta>/`.
- `solo_humano`: status que solo una persona puede poner (el agente nunca los asigna). Los scripts lo exigen: `--humano` y además una terminal interactiva o `UXYNGRAPHAR_HUMANO=1` (nunca con `CI`); el agente no tiene ninguna de las dos.
- `espera_humano`: status en los que la ficha espera una decisión de una persona (los recoge `revision-humana`); por defecto, `inicial` si no está en `solo_humano`.
- `comandos`: `{status: "scripts/… {id} …"}` para los status que no se ponen con `fichas.py estado` (p. ej. `approved` → `scripts/ciclo.py aprobar {id} --humano`).
- `variantes`: `{nombre: "plantillas/….md"}` plantillas alternativas del tipo (`fichas.py nueva <tipo> --variante <nombre>`).
- Id de ficha nueva: `<PREFIJO>-<AAAAMMDD>-<slug>`.
- No son fichas: `INDICE.md`, `README.md`, `RESUMEN.md`, `ESTADO.md`, lo que empieza por `_` y los `.md` con nombre en MAYÚSCULAS sin `id` en el frontmatter (índices, registros, matrices, informes). `CONTEXTO.md` con `id` sí lo es.
- Las plantillas usan `{{id}}`, `{{fecha}}`, `{{titulo}}`, `{{status}}`.

## 4. `INTEGRIDAD.json`

```json
{"formato": 1, "algoritmo": "sha256", "paquete": "<id>", "version": "X.Y.Z", "archivos": {"<ruta>": "<sha256>"}}
```

Cubre todos los archivos del paquete salvo el propio `INTEGRIDAD.json`, `__pycache__/` y `*.pyc`. `scripts/comun/verificar-integridad.py` informa de archivos alterados, faltantes y añadidos; cualquiera de ellos es un fallo y el agente se detiene.

## 5. `FLUJO.json`

```json
{"formato": 1, "modo": "manual", "leer_por_defecto": [], "trabajar_con": null, "secuencia": [], "conflictos": "preguntar"}
```

| Modo | Comportamiento del agente |
|------|---------------------------|
| `manual` | Solo usa paquetes nombrados en el pedido. |
| `leer_por_defecto` | En cada pedido lee el `README.md` de `leer_por_defecto`; aplica solo los nombrados. |
| `trabajar_con` | Paquete base: aplica `trabajar_con` en cada pedido aunque no lo nombre, y además los que el pedido nombre; también lee `leer_por_defecto`. Se fija al instalar con `--base <id>` (la migración desde 1.x deja `instrucciones-aprobadas`, que en 1.x era obligatorio). |
| `secuencia` | Recorre `secuencia` en orden (cada paquete con su `README.md` y sus verificaciones); también lee `leer_por_defecto`. |

- Un paquete nombrado en el pedido siempre se aplica, sea cual sea el modo.
- `conflictos: "preguntar"`: si dos paquetes activos se contradicen, el agente se detiene y pregunta.
- Todo id citado debe estar instalado.

## 6. Activación

El agente activa un paquete cuando el pedido contiene «usa el paquete <frase>» o «sigue el protocolo <frase>», con `<frase>` en `activacion`, o cuando `FLUJO.json` lo indica. El bloque de entrada del README, generado desde el manifiesto, fija el orden:

1. `python3 uxyngraphar/paquetes/<id>/scripts/comun/verificar-integridad.py` → si falla, detenerse y avisar.
2. Leer `PAQUETE.md`: si el pedido cae en «Fuera de alcance», decirlo y proponer el paquete indicado.
3. Si hay `limites`: leer `LIMITES.md`.
4. Si hay `proceso`: recorrer las fases en orden; cada fase cita las skills que usa.
5. Si hay `skills`: leer cada `SKILL.md` cuando una fase la cite o el pedido encaje con su descripción.
6. Consultar `COMPONENTES.md`, `HERRAMIENTAS.md`, `referencia/` y `ejemplos/` cuando haga falta.
7. Si hay `andamiaje`: `scripts/comun/andamiar.py <variante> --nombre <n>` simula; `--aplicar` crea sin sobrescribir (también `uxyngraphar andamiar <id> …` desde el motor).
8. Escribir solo en `uxyngraphar/trabajo/<id>/` y, en el código, solo lo que el pedido pida.
9. Ejecutar las `verificaciones` del manifiesto antes de terminar.

### 6.1 Protecciones

Cada instalación, actualización o desinstalación regenera, a partir de los paquetes instalados (`motor/protecciones.py`):

- `.claude/settings.json` → `permissions.deny`: `Edit`/`Write` sobre `uxyngraphar/paquetes/**`, `FLUJO.json`, `INDICE.md`, `trabajo/*/ajustes.json` y los `protegidos` de cada paquete; y `Bash` con `UXYNGRAPHAR_HUMANO`. Las reglas del proyecto se conservan.
- `.cursorignore` (y `.geminiignore`, `.aiexclude` si existen) → bloque entre marcas con los `fuera_de_ia`; el archivo se borra si queda vacío.

Sin paquetes instalados no queda ninguna regla propia.

## 7. Nomenclatura

Los nombres de los paquetes del kit (ids, títulos, familia, tipos, prefijos de 3 letras únicos, status, frases de activación, scripts y archivos) siguen `motor/NOMENCLATURA.md`, con vocabulario y excepciones en `motor/nomenclatura.json`. `validar` y `crear` la comprueban; `uxyngraphar nomenclatura` lista los status heredados pendientes de migrar. La norma es del kit: no se aplica a los proyectos donde se instalan los paquetes.

## 8. Versionado

- Cada paquete tiene su semver: MAYOR si cambia la forma del trabajo (`fichas`, carpetas) o si quita una pieza o un problema del alcance; MENOR si añade una pieza, una fase, una skill, reglas o guías; PARCHE si corrige.
- Cada cambio de versión se anota en `CHANGELOG.md` (pieza `cambios`).
- Actualizar reemplaza `uxyngraphar/paquetes/<id>/` completo; nunca toca `uxyngraphar/trabajo/`.
- Un cambio MAYOR que exija mover trabajo lo hace el motor con respaldo, nunca el paquete.

## 9. Migración desde 1.x

`uxyngraphar migrar --repo RUTA` busca instalaciones 1.x (`.uxyngraphar.lock` o numeración `00-nucleo`/`05-instrucciones`) en `docs/` o `uxyngraphar/` (hasta 4 niveles) y **solo simula**; `--aplicar` migra.

- Se bloquea (sin tocar nada) si no hay lock, si hay un archivo que la clasificación 1.x no cubre, un archivo de núcleo distinto del lock, `uxyngraphar/` junto a `docs/` o una carpeta `.uxyngraphar-migrando/` de una migración interrumpida.
- Contenido del proyecto (clases P/M/C) → `uxyngraphar/trabajo/<paquete>/` según la tabla de `migrar.DESTINOS` (`05-instrucciones/` → `instrucciones-aprobadas/instrucciones/`, `20-decisiones/` → `decisiones-de-arquitectura/`, `15-rutas/` → `rutas-de-api/` o `paginas-de-interfaz/`, `46-…` → `evolucion-del-sistema/`, `03-preguntas/` → `preguntas-de-clarificacion/preguntas/`, `90-archivo/` → `documentos-archivados/archivo/`, `95-memoria/` → `notas-de-memoria/memoria/`, `96-…` → `reglas-del-proyecto/reglas/`, `97-…` → `adaptaciones-de-paquetes/ajustes-locales/`, `00-nucleo/arquitectura.md` y `restricciones.md` → `arquitectura-monolitica-por-capas/`, `registro-ids-compartidos.md` → `contratos-entre-repositorios/REGISTRO-1X.md`, `glosario-dominio.md` → `idiomas-del-codigo/GLOSARIO.md`, `ESTADO.md` → `instrucciones-aprobadas/`, …); los status 1.x se adaptan a los 2.0 (`executing` → `approved`, `archivada` → `archived`…); `mapa-capas.md`, `vision-espejo.md` y `plantilla-modulo.md` editados van a su paquete en vez de bloquear; `0N-estado/<fecha>/x.md` pasa a `estado/x.md` (con la fecha delante solo si dos archivos chocan); lo que no tiene paquete y los artefactos locales (X: tokens de aprobación, lock) → `uxyngraphar/trabajo/_legado-1x/`. `uxyngraphar.config.json` se reparte en `ajustes.json`.
- Al aplicar: respaldo en `.uxyngraphar-respaldos/migracion-<fecha>/` (pack, AGENTES/AGENTS/CLAUDE, `.claude/settings.json`, CODEOWNERS, guardia de Cursor, exclusiones de IA, ganchos git, workflow `uxyngraphar.yml`) → copia a `.uxyngraphar-migrando/` → verificación sha256 → retirada del pack 1.x y de sus protecciones → el trabajo pasa a `uxyngraphar/trabajo/` (también cuando el pack 1.x vivía en `uxyngraphar/`) → instalación de los paquetes equivalentes (`migrar.COMUNES` más el de rutas que corresponda) (`arquitectura-monolitica-por-capas` con el perfil del pack) con `FLUJO.json` en `trabajar_con` = `instrucciones-aprobadas`. Cualquier fallo restaura el estado anterior desde el respaldo.
- `.gitignore`/`.gitattributes` con líneas del pack 1.x solo se avisan.
