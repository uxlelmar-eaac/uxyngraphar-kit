# Especificación del protocolo de sistemas — versión 1

Esta es la versión 1 del **protocolo** de sistemas de gobernanza (manifiesto `manifiesto_formato` 1, `FLUJO.json` formato 1). Su núcleo obligatorio incluye las **memorias** (`MEMORIAS.md` y `scripts/comun/memorias.py`) y los **límites y permisos** (`LIMITES.md`, `PERMISOS.md` y el campo `permisos`). Es independiente de la versión de la **herramienta** (`motor/VERSION`, hoy 1.x): la herramienta puede publicar versiones nuevas sin cambiar el protocolo, y el protocolo solo cambia de versión cuando un sistema o un `FLUJO.json` válidos dejan de serlo.

Validadores: [`especificacion.py`](especificacion.py) (sistema y flujo), [`piezas.py`](piezas.py) (una función por pieza estándar) y [`sistemas-de-gobernanza/_base/scripts/comun/uxyn_base.py`](../sistemas-de-gobernanza/_base/scripts/comun/uxyn_base.py) (manifiesto e integridad; cada sistema lleva su propia copia en `scripts/comun/`).

## 1. Estructura en un repo

```
<raiz-app>/
  AGENTES.md · AGENTS.md · CLAUDE.md   el mismo bloque generado entre <!-- uxyngraphar:inicio --> y <!-- uxyngraphar:fin -->
  uxyngraphar/                    todo uxyngraphar en una sola carpeta
    INDICE.md                     generado por el motor
    FLUJO.json                    lo edita solo una persona
    sistemas-de-gobernanza/<id>/                un sistema (inmutable; lo escribe solo el motor)
    trabajo/<id>/                 trabajo de cada sistema (editable)
      ajustes.json                opcional: sobrescribe «ajustes» del manifiesto
      memorias/MEM-…md            memorias del proyecto para ese sistema (§2.3); las propone el agente, las aprueba la persona
      <estado>/<ficha>.md         sistema con un solo tipo de ficha (p. ej. decisiones-de-arquitectura/completadas/ADR-…md)
      <tipo>/<estado>/<ficha>.md  tipo con carpeta propia (p. ej. instrucciones-aprobadas/instrucciones/pendientes/INS-…md)
```

Sin números delante de las carpetas ni carpetas por fecha: la fecha va en el id de la ficha.

Un sistema resuelve su trabajo como `<carpeta-del-sistema>/../../trabajo/<id>/`.

## 2. Sistema: el protocolo

La base (`sistemas-de-gobernanza/_base/`) es un **protocolo**, no un molde: fija cómo se organiza un sistema, no qué tiene que contener. Cada sistema es un monolito autosuficiente y especializado (un conjunto acotado de problemas o acciones): copiar su carpeta a otro `uxyngraphar/sistemas-de-gobernanza/` basta para usarlo, y cada pieza se agrega, mejora o quita sin tocar las demás. Tres niveles:

**Nivel 1. Núcleo obligatorio** (lo único que da errores si falta):

```
<id>/
  sistema.json                    manifiesto (§3): identidad, alcance, piezas y extensiones
  README.md                       entrada del agente: bloque generado entre <!-- uxyngraphar:entrada:inicio --> y
                                  <!-- uxyngraphar:entrada:fin --> a partir del manifiesto; el resto es libre del autor
  SISTEMA.md                      ficha de descripción (§2.1)
  MEMORIAS.md                     qué conviene recordar del proyecto al trabajar con el sistema (§2.3)
  LIMITES.md                      reglas duras y cuándo detenerse a preguntar (§2.4)
  PERMISOS.md                     qué hace el agente solo, qué decide una persona y qué rutas no toca (§2.4)
  scripts/comun/                  infraestructura común (nace de sistemas-de-gobernanza/_base): uxyn_base.py, uxyn_fichas.py, fichas.py,
                                  uxyn_memorias.py, memorias.py, uxyn_permisos.py, verificar.py, verificar-integridad.py,
                                  andamiar.py
  INTEGRIDAD.json                 solo en sistemas construidos/instalados (§4)
```

**Nivel 2. Piezas estándar** (opcionales; se declaran en «piezas»; si existen, siguen su forma — §2.2):

| Pieza | Ruta | Forma |
|-------|------|-------|
| `proceso` | `proceso/<fase>.md` | una fase por archivo, en el orden de «proceso»; frontmatter `fase`, `resuelve`, `skills`; secciones «Objetivo», «Pasos», «Criterio de salida» (y «Entradas») |
| `skills` | `skills/<nombre>/SKILL.md` | frontmatter `name` (= carpeta), `description`, `resuelve`; secciones «Cuándo usarla», «Pasos» (y «Resultado»); la carpeta puede llevar más archivos |
| `componentes` | `COMPONENTES.md` | `# Componentes`; una sección `## <componente>` por pieza conceptual |
| `herramientas` | `HERRAMIENTAS.md` | `# Herramientas`; documenta cada script ejecutable de `scripts/` (aviso si falta alguno) |
| `andamiaje` | `andamiaje/<variante>/` | una carpeta por variante de «andamiaje»; `__nombre__` en rutas; `{{nombre}}`, `{{Nombre}}`, `{{nombreCamel}}` en el contenido; los archivos que no son `.md` llevan el sufijo `.plantilla`, que se quita al crearlos (el typecheck y los linters del proyecto no los toman por código) |
| `plantillas` | `plantillas/` | plantillas de fichas (§3.1) y documentos que el sistema copia al trabajo |
| `referencia` | `referencia/` | guías de consulta (`.md`) |
| `ejemplos` | `ejemplos/` | casos resueltos de principio a fin (`.md`) |
| `pruebas` | `pruebas/test_*.py` | pruebas propias con `unittest`, ejecutables desde la carpeta del sistema sin el motor |
| `cambios` | `CHANGELOG.md` | `# Cambios`; una sección `## X.Y.Z` por versión (aviso si falta la actual) |

**Nivel 3. Extensiones libres:** carpetas o archivos de primer nivel propios del sistema, declarados en «extensiones» con una frase de para qué sirven. Solo cumplen las reglas de portabilidad.

Cualquier otra entrada de primer nivel es un error: o es una pieza estándar, o se declara como extensión. Los scripts propios del sistema van en `scripts/` (fuera de `scripts/comun/`).

### 2.1 `SISTEMA.md`

Empieza por `# <título>` y una o dos frases de lo que garantiza. Secciones obligatorias: «Qué resuelve», «Problemas que cubre» (cita cada id de `alcance.problemas` entre comillas invertidas), «Fuera de alcance», «Cuándo usarlo», «Entradas y salidas». Recomendadas: «Cuándo no usarlo», «Sistemas complementarios».

### 2.2 Errores y avisos

El validador separa lo que rompe el sistema de lo que solo orienta:

- **Errores:** falta un archivo del núcleo; marcadores `{{…}}` en el núcleo (`sistema.json`, `README.md`, `SISTEMA.md`, `MEMORIAS.md`, `LIMITES.md`, `PERMISOS.md`); secciones obligatorias de `SISTEMA.md`, `MEMORIAS.md` o `LIMITES.md`; bloque de `PERMISOS.md` desfasado; `permisos` inválido o que cita scripts inexistentes; `limites` en «piezas» o `protegidos`/`fuera_de_ia` sueltos; un tipo de ficha con carpeta `memorias` o prefijo `MEM`; bloque de entrada del README desfasado (`uxyngraphar indice-sistema <id>` lo regenera); una pieza declarada que falta o no sigue su forma; una pieza presente sin declarar; una fase o skill citada que no existe; un `resuelve` que cita un problema inexistente; una extensión declarada que falta; una entrada de primer nivel no declarada; portabilidad.
- **Avisos:** más de 5 problemas (posible sistema generalista); un problema que no cubre ninguna fase ni skill; una skill sin `resuelve`; piezas recomendadas para la familia que faltan; marcadores en piezas opcionales; scripts sin documentar en `HERRAMIENTAS.md`; `scripts/comun/` distinto de `_base`.

`uxyngraphar validar --completitud` muestra, por sistema, las piezas presentes, las recomendadas que faltan y las extensiones.

### 2.3 Memorias

Cada sistema lleva en su núcleo `MEMORIAS.md`: empieza por `# Memorias`, una o dos frases y las secciones obligatorias «Qué recordar» y «Qué no recordar», con la guía propia del tema (qué dato del proyecto necesita el sistema y se pierde entre conversaciones, y qué no vale la pena memorizar porque ya vive en fichas, código u otro sistema).

Las memorias de cada proyecto viven en `uxyngraphar/trabajo/<id>/memorias/<MEM-AAAAMMDD-slug>.md` (fuera del sistema, que es inmutable) y se gestionan con `scripts/comun/memorias.py` (`listar [--vigentes|--status S] [--json]`, `ver`, `nueva`, `aprobar --humano`, `archivar --humano`). Frontmatter:

```yaml
id: MEM-20261111-orm-sin-migraciones
status: propuesta          # propuesta | vigente | archivada
fecha: 2026-11-11
autor: agente              # agente | persona
fuente: "pedido del 11/11"
valida_hasta: null         # AAAA-MM-DD opcional; caducada = no se aplica
aprobada_por: persona      # la pone `aprobar` en las memorias del agente
```

- El agente las lee **siempre** al activar el sistema (paso del bloque de entrada, §6), aplica las vigentes no caducadas y trata las propuestas solo como contexto.
- El agente solo crea memorias `propuesta`. `vigente` y `archivada` son de la persona (`--humano`, como `solo_humano` en §3.1, o el panel). Las que crea la persona con `--humano` nacen `vigente`.
- `verificar.py` valida id, status, autor y que ninguna memoria del agente esté vigente sin `aprobada_por: persona`; avisa de las vigentes caducadas.
- La carpeta `memorias` y el prefijo `MEM` están reservados: ningún tipo de ficha los usa y `fichas.py` no lista lo que hay en `memorias/`.

### 2.4 Límites y permisos

Cada sistema lleva en su núcleo:

- `LIMITES.md`: empieza por `# Límites`, al menos una regla dura numerada («1. …») y la sección obligatoria «## Cuándo detenerse y preguntar». Las reglas se cumplen en todo el trabajo; romper una lo decide una persona.
- `PERMISOS.md`: empieza por `# Permisos`; lleva un bloque entre `<!-- uxyngraphar:permisos:inicio -->` y `<!-- uxyngraphar:permisos:fin -->` generado desde `permisos` del manifiesto (§3; `uxyngraphar indice-sistema <id>` lo regenera junto con el del README) con tres secciones: «El agente puede», «Solo una persona» y «Rutas». El resto es del autor (p. ej. «## Por qué»).

Reglas:

- **Solo una persona**, además de lo declarado en `permisos.acciones.solo_persona`: `memorias.py aprobar|archivar` y los status `solo_humano` de cada tipo de ficha (§3.1). El agente no las ejecuta: se detiene y se las pide a la persona.
- **El agente puede**, además de lo declarado en `permisos.acciones.agente`: `memorias.py listar|ver|nueva` y, si hay fichas, `fichas.py nueva|estado` salvo los status de la persona.
- Una acción es `scripts/….py [subcomando]`; declarada sin subcomando cubre todo el script. No puede estar a la vez en `agente` y `solo_persona`.
- Los scripts propios llaman a `uxyn_permisos.exigir(sistema, "scripts/x.py subcomando")` antes de una acción de la persona: si no la ejecuta una persona (terminal interactiva o `UXYNGRAPHAR_HUMANO=1`), falla con `PermissionError`. El validador avisa de un script con acciones `solo_persona` que nunca llama a `exigir`.
- **Rutas** (relativas a `trabajo/<id>/`): `protegidas` → reglas `deny` de escritura; `fuera_de_ia` → exclusiones de IA (§6.1). `ajustes.json` siempre está protegido.
- `verificar.py` comprueba que `LIMITES.md` y `PERMISOS.md` existen, que el bloque de permisos está al día y que los scripts citados existen.

### 2.5 Portabilidad

- Ningún script importa nada de fuera de la carpeta del sistema ni supone rutas fijas del repo.
- Ningún script escribe fuera de `uxyngraphar/trabajo/<id>/`, salvo el andamiaje (en el destino declarado, sin sobrescribir) o una ruta explícita de la persona.
- Sin integración continua: ni la instalación, ni la actualización, ni ningún sistema crean workflows ni archivos de CI (`.github/`, `.gitlab-ci.yml`, `.forgejo/`…) en el repo de destino. Todo se ejecuta en local y bajo pedido, así que instalar el kit en muchos repos no consume minutos de Actions.
- Nombres de archivo ASCII y sin espacios; Python solo con librería estándar.
- Copiar la carpeta a otro `uxyngraphar/sistemas-de-gobernanza/` produce el mismo comportamiento.

`sistemas-de-gobernanza/_base/` guarda el núcleo de partida y, en `piezas/<pieza>/`, la semilla de cada pieza estándar (sus archivos y, si la pieza añade campos al manifiesto, un `manifiesto.json` con ellos). No es un sistema: el catálogo lo ignora, no se construye ni se instala. `crear` copia el núcleo y las piezas pedidas; `pieza <id> agregar|quitar <pieza>` añade o retira una pieza después.

## 3. Manifiesto `sistema.json`

| Campo | Tipo | Regla |
|-------|------|-------|
| `manifiesto_formato` | entero | `1` |
| `id` | texto | kebab-case ASCII; igual al nombre de la carpeta; cumple `NOMENCLATURA.md` |
| `version` | texto | semver `X.Y.Z` |
| `titulo`, `descripcion` | texto | no vacíos; título = id en lenguaje natural (`NOMENCLATURA.md`) |
| `familia` | texto | `proceso`, `codigo`, `arquitectura`, `documentacion`, `seguridad`, `producto` o `plataforma` |
| `motor` | texto | `>=X.Y`; versión mínima del motor |
| `activacion` | lista | frases que activan el sistema: el `id`, el id con espacios y otras sin repetir ni contener las de otro sistema |
| `entrada` | texto | `README.md` |
| `verificaciones` | lista | `scripts/*.py` que el agente ejecuta antes de cerrar (la genérica: `scripts/comun/verificar.py`) |
| `fichas` | objeto | opcional; tipos de ficha (§3.1) |
| `ajustes` | objeto | opcional; valores por defecto que el proyecto puede sobrescribir en `ajustes.json` |
| `permisos` | objeto | obligatorio; `{rutas: {protegidas, fuera_de_ia}, acciones: {agente, solo_persona}}`: globs relativos a `trabajo/<id>/` que la IA no edita (reglas `deny` de Claude) o no lee (`.cursorignore` y equivalentes), y acciones `scripts/….py [subcomando]` (§2.4). Los campos sueltos `protegidos` y `fuera_de_ia` no se aceptan |
| `al_activar_sistema` | texto | opcional; `scripts/… {id}` que el agente ejecuta al activar cualquier sistema (`{id}`: el activado) |
| `alcance` | objeto | `problemas`: lista no vacía de `{id, descripcion}` (ids kebab-case únicos); `fuera_de_alcance`: lista no vacía de `{tema, derivar_a}` (`derivar_a`: id de sistema o `null`) |
| `piezas` | lista | piezas estándar presentes (§2), sin repetir; puede estar vacía |
| `proceso` | lista | solo con la pieza `proceso`: fases en orden (kebab-case), una por `proceso/<fase>.md` |
| `andamiaje` | objeto | solo con la pieza `andamiaje`: `{variante: {descripcion, destino}}`; `destino` relativo a la raíz de la app, admite `{nombre}` |
| `extensiones` | objeto | opcional; `{ruta-de-primer-nivel: para qué sirve}` |
| `editor` | texto | opcional; kebab-case; quién publica el sistema en el servidor (por defecto `uxyngraphar`) |
| `idioma` | texto | opcional; código de dos letras (por defecto `es`) |
| `licencia` | texto | opcional; expresión SPDX o `propietaria` (por defecto `CC-BY-4.0`) |
| `etiquetas` | lista | opcional; hasta 12, kebab-case; ayudan a encontrarlo en el servidor |
| `repositorio` | texto | opcional; URL https de la fuente |

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
"ruta": {"carpeta": ".", "prefijo": "RUT", "plantilla": "plantillas/ruta.md", "inicial": "activa", "status_validos": ["activa", "reemplazada"]}
```

- `carpeta`: `.` (raíz del trabajo del sistema; solo si hay un único tipo) o un nombre kebab-case.
- Con `estados`: la ficha vive en `uxyngraphar/trabajo/<id>/<carpeta>/<carpeta-de-estado>/<ficha>.md`; las carpetas de estado son kebab-case sin números (`pendientes`, `en-progreso`, `completadas`, `archivadas`, `canceladas`, `para-eliminar`) y el `status` debe corresponder a la carpeta.
- Con `status_validos` (plana): vive en cualquier subruta de `<carpeta>/`.
- `solo_humano`: status que solo una persona puede poner (el agente nunca los asigna). Los scripts lo exigen: `--humano` y además una terminal interactiva o `UXYNGRAPHAR_HUMANO=1` (nunca con `CI`); el agente no tiene ninguna de las dos.
- `espera_humano`: status en los que la ficha espera una decisión de una persona (los recoge `revision-humana`); por defecto, `inicial` si no está en `solo_humano`.
- `comandos`: `{status: "scripts/… {id} …"}` para los status que no se ponen con `fichas.py estado` (p. ej. `aprobada` → `scripts/ciclo.py aprobar {id} --humano`).
- `variantes`: `{nombre: "plantillas/….md"}` plantillas alternativas del tipo (`fichas.py nueva <tipo> --variante <nombre>`).
- Id de ficha nueva: `<PREFIJO>-<AAAAMMDD>-<slug>`.
- No son fichas: `INDICE.md`, `README.md`, `RESUMEN.md`, `ESTADO.md`, lo que empieza por `_` y los `.md` con nombre en MAYÚSCULAS sin `id` en el frontmatter (índices, registros, matrices, informes). `CONTEXTO.md` con `id` sí lo es.
- Las plantillas usan `{{id}}`, `{{fecha}}`, `{{titulo}}`, `{{status}}`.

## 4. `INTEGRIDAD.json`

```json
{"formato": 1, "algoritmo": "sha256", "sistema": "<id>", "version": "X.Y.Z", "archivos": {"<ruta>": "<sha256>"}}
```

Cubre todos los archivos del sistema salvo el propio `INTEGRIDAD.json`, `__pycache__/` y `*.pyc`. `scripts/comun/verificar-integridad.py` informa de archivos alterados, faltantes y añadidos; cualquiera de ellos es un fallo y el agente se detiene.

### 4.1 Artefacto (lo que se publica en el servidor)

`<id>-<version>.zip` con una sola carpeta raíz `<id>/` que contiene el sistema construido (con `INTEGRIDAD.json`).
Reproducible: fecha 1980-01-01, entradas en orden, permisos 0644 (0755 los `.py`). Quien lo recibe rechaza rutas
absolutas o con `..`, `\`, enlaces, nombres no ASCII o con espacios, más de una raíz, cifrado, más de 2000 archivos o
más de 50 MB descomprimido, y lo valida como construido. La sha256 del zip es la que publica el índice del servidor
(ADR 0007 y 0008).

## 5. `FLUJO.json`

```json
{"formato": 1, "modo": "manual", "leer_por_defecto": [], "trabajar_con": null, "secuencia": [], "conflictos": "preguntar"}
```

| Modo | Comportamiento del agente |
|------|---------------------------|
| `manual` | Solo usa sistemas nombrados en el pedido. |
| `leer_por_defecto` | En cada pedido lee el `README.md` de `leer_por_defecto`; aplica solo los nombrados. |
| `trabajar_con` | Sistema base: aplica `trabajar_con` en cada pedido aunque no lo nombre, y además los que el pedido nombre; también lee `leer_por_defecto`. Se fija al instalar con `--base <id>`. |
| `secuencia` | Recorre `secuencia` en orden (cada sistema con su `README.md` y sus verificaciones); también lee `leer_por_defecto`. |

- Un sistema nombrado en el pedido siempre se aplica, sea cual sea el modo.
- `conflictos: "preguntar"`: si dos sistemas activos se contradicen, el agente se detiene y pregunta.
- Todo id citado debe estar instalado.

## 6. Activación

El agente activa un sistema cuando el pedido contiene «usa el sistema de gobernanza <frase>», «usa el sistema <frase>» o «sigue el protocolo <frase>», con `<frase>` en `activacion`, o cuando `FLUJO.json` lo indica. El bloque de entrada del README, generado desde el manifiesto, fija el orden:

1. `python3 uxyngraphar/sistemas-de-gobernanza/<id>/scripts/comun/verificar-integridad.py` → si falla, detenerse y avisar.
2. Leer `SISTEMA.md`: si el pedido cae en «Fuera de alcance», decirlo y proponer el sistema indicado.
3. Memorias: leer `MEMORIAS.md` y `scripts/comun/memorias.py listar`; aplicar las vigentes; proponer lo que valga la pena recordar con `memorias.py nueva` (nunca aprobar ni archivar).
4. Límites y permisos: leer `LIMITES.md` y `PERMISOS.md`; no ejecutar las acciones de «Solo una persona» ni tocar las rutas excluidas: detenerse y pedírselo a la persona.
5. Si hay `proceso`: recorrer las fases en orden; cada fase cita las skills que usa.
6. Si hay `skills`: leer cada `SKILL.md` cuando una fase la cite o el pedido encaje con su descripción.
7. Consultar `COMPONENTES.md`, `HERRAMIENTAS.md`, `referencia/` y `ejemplos/` cuando haga falta.
8. Si hay `andamiaje`: `scripts/comun/andamiar.py <variante> --nombre <n>` simula; `--aplicar` crea sin sobrescribir (también `uxyngraphar andamiar <id> …` desde el motor).
9. Escribir solo en `uxyngraphar/trabajo/<id>/` y, en el código, solo lo que el pedido pida.
10. Ejecutar las `verificaciones` del manifiesto antes de terminar.

### 6.1 Protecciones

Cada instalación, actualización o desinstalación regenera, a partir de los sistemas instalados (`motor/protecciones.py`):

- `.claude/settings.json` → `permissions.deny`: `Edit`/`Write` sobre `uxyngraphar/sistemas-de-gobernanza/**`, `FLUJO.json`, `INDICE.md`, `trabajo/*/ajustes.json` y las `permisos.rutas.protegidas` de cada sistema; y `Bash` con `UXYNGRAPHAR_HUMANO`. Las reglas del proyecto se conservan.
- `.cursorignore` (y `.geminiignore`, `.aiexclude` si existen) → bloque entre marcas con las `permisos.rutas.fuera_de_ia`; el archivo se borra si queda vacío.

Sin sistemas instalados no queda ninguna regla propia.

## 7. Nomenclatura

Los nombres de los sistemas del kit (ids, títulos, familia, tipos, prefijos de 3 letras únicos, status, frases de activación, scripts y archivos) siguen `motor/NOMENCLATURA.md`, con vocabulario y excepciones en `motor/nomenclatura.json`. `validar` y `crear` la comprueban; `uxyngraphar nomenclatura` lista los status heredados pendientes de pasar al vocabulario. La norma es del kit: no se aplica a los proyectos donde se instalan los sistemas.

## 8. Versionado

- Cada sistema tiene su semver: MAYOR si cambia la forma del trabajo (`fichas`, carpetas) o si quita una pieza o un problema del alcance; MENOR si añade una pieza, una fase, una skill, reglas o guías; PARCHE si corrige.
- Cada cambio de versión se anota en `CHANGELOG.md` (pieza `cambios`).
- Actualizar reemplaza `uxyngraphar/sistemas-de-gobernanza/<id>/` completo; nunca toca `uxyngraphar/trabajo/`.
- Un cambio MAYOR que exija mover trabajo lo hace el motor con respaldo, nunca el sistema.

## 9. `verificar --formato json`

`uxyngraphar verificar --repo RUTA --formato json [--trabajos N] [--segundos S]` escribe un único objeto JSON, estable dentro del formato 1:

```json
{"formato": 1, "repo": "/ruta/absoluta", "codigo": 0,
 "resultados": [{"sistema": "rutas-de-api", "verificacion": "scripts/comun/verificar-fichas.py", "codigo": 0, "salida": "…"}]}
```

- `resultados`: una entrada por verificación de cada sistema instalado, en el orden de los sistemas y de su manifiesto (también con `--trabajos` > 1).
- `codigo` de cada verificación: el de su proceso; 124 si agotó `--segundos`.
- `codigo` total, que es también el código de salida: **0** todo bien, **1** alguna verificación encontró problemas, **2** alguna no se pudo ejecutar (agotó el tiempo, la mató una señal o terminó con un traceback).

La integración opcional en CI (`.github/workflows/uxyngraphar-verificar.yml`) y el gancho `pre-commit` se añaden y se quitan desde el panel o con `uxyngraphar integracion agregar|quitar workflow|precommit`; nunca se instalan por defecto y `retirar` los quita. Solo se tocan archivos con la marca `uxyngraphar-integracion`.

