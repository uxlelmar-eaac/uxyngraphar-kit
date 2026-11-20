# Cambios

## 1.6.4

- **Capas de uxyngraphar en la revisión de archivos**: cada archivo y carpeta del árbol lleva el tono de su capa, con
  una leyenda arriba (cuántos hay de cada una) y una insignia junto al nombre del archivo abierto:
  - **Núcleo** (dorado): `sistema.json`, `README.md`, `SISTEMA.md`, `MEMORIAS.md`, `LIMITES.md`, `PERMISOS.md` e
    `INTEGRIDAD.json`.
  - **Estándar** (verde): las piezas estándar (`proceso/`, `skills/`, `COMPONENTES.md`, `HERRAMIENTAS.md`,
    `andamiaje/`, `plantillas/`, `referencia/`, `ejemplos/`, `pruebas/`, `CHANGELOG.md`).
  - **Común** (melocotón): `scripts/comun/`, los scripts del motor iguales en todos los sistemas.
  - **Propio** (neutro): las extensiones y todo lo demás del sistema.
  Las listas son las de `_base/scripts/comun/uxyn_base.py` y una prueba comprueba que siguen iguales. Igual en la web.

## 1.6.3

- **Revisar archivos**, a pantalla completa (`#/revision?id=…`, desde «Mis sistemas»): árbol de carpetas a la izquierda,
  el archivo en el centro y tus notas y resaltados a la derecha, sin el menú lateral para leer con calma. Al
  seleccionar texto aparece un menú con tres herramientas:
  - **Mejorar**: la IA reescribe solo ese fragmento (con el archivo como contexto), ves el antes y el después y lo
    aplicas en el archivo si te convence (`POST /api/creador/mejorar-fragmento`).
  - **Añadir nota** y **Resaltar**: quedan guardados en `.anotaciones.json` del catálogo, fuera del sistema (no cambian
    su validación, su zip ni lo que se instala). Se pueden resolver, reabrir y borrar
    (`/api/anotaciones`, `/api/anotaciones/crear|cambiar|borrar`).
- **uxyn usa tus notas**: «Pedir a uxyn que use mis notas» (en la revisión) y la sugerencia «Usar mis notas (N)» del
  panel de uxyn le mandan tus notas y resaltados abiertos como guía; sus cambios llegan a «Por revisar». El texto del
  pedido es el mismo que en la web.
- «Ver archivos» de Mis sistemas pasa a ser «Revisar archivos» y abre esa pantalla.

## 1.6.2

- **Mis sistemas → «Ver archivos»**: cada sistema del equipo muestra su estructura completa, carpetas y archivos, con
  qué es cada pieza (núcleo, `proceso/`, `skills/`, `config/`…), cuántas carpetas y archivos tiene y una vista previa
  de solo lectura (Markdown legible). «Abrir en el Taller» lleva al paso de ese archivo y lo abre en el editor
  (`#/creador?id=…&archivo=…`).
- **Panel de uxyn en el Taller**, más limpio: arriba solo el modo (uxyn | Simulador) y el historial, que solo aparece si
  hay conversaciones; el hilo ocupa el espacio; debajo, tres sugerencias («Completar el sistema», «Revisar el sistema»,
  «Mejorar el archivo abierto»), la caja de mensaje y la IA elegida en una línea. Fuera los textos repetidos sobre
  «Por revisar».

## 1.6.1

- `importar --modo crear`: si el material ya trae sus ejemplos (`ejemplos/`), el ejemplo de arranque con marcadores
  se retira como ya se hacía con `proceso/` y `skills/`. Un sistema completo importado como «crear» queda
  implementado sin tener que borrar a mano el caso de ejemplo de la base.
- Importar un JSON de `config/` que la base no amplía conserva sus bytes tal cual (también en Windows).

## 1.6.0

Núcleo implementado: un sistema de gobernanza ya no puede salir de uxyn como un esqueleto, el material de la persona
llega entero y el sistema instalado mejora sin editarlo.

- Compuerta **implementado** (`uxyngraphar validar <id> --implementado`, también en `creador validar`, en
  `importar` y en el panel con la insignia «Implementado ✓»): exige contenido real en el núcleo (rol del agente,
  problemas explicados, al menos 5 límites comprobables y 3 casos de «detente y pregunta», memorias, permisos), al
  menos una fase, una skill, un ejemplo y el CHANGELOG, y prohíbe citar archivos de otro sistema (solo flujos). Los
  avisos de calidad (núcleo de menos de 9 KB, menos de 3 fases o 2 skills) solo se muestran. ESPECIFICACION.md §2.6.
- `importar --modo auto|crear|adaptar`: «adaptar» conserva id, versión y todos los archivos y solo añade o adapta el
  núcleo (cero cambios fuera del núcleo y del manifiesto); «crear» ya no deja fases ni skills de arranque cuando la
  persona trae las suyas. Las dos devuelven el **informe de preservación** (N/N, sha256 por archivo) y se cancelan si
  se perdiera alguno. El origen nunca se toca.
- «Empezar con uxyn» con archivos, carpeta o zip: primero se importan sin pérdidas y uxyn trabaja sobre el sistema
  importado, en vez de reescribir el material desde el chat. Fuera la frase «archivos núcleo» del mensaje a uxyn.
- Propuestas de mejora: `scripts/comun/mejoras.py` (nueva, listar, ver) escribe
  `uxyngraphar/trabajo/<id>/propuestas-de-mejora/PMS-….md` (carpeta y prefijo reservados), con diff opcional solo de
  archivos del sistema; `uxyngraphar reportar <id> --mejora PMS-…` la envía al autor con vista previa (hasta 12 000
  caracteres; servidor 1.1.0). AGENTES.md lo indica a los agentes.
- La base trae «Rol del agente» en SISTEMA.md, la regla «No edites este sistema» y huecos para 5 límites, 3 casos de
  «detente y pregunta» y 3 + 2 memorias.
- Mercado del panel: estrellas, valoración e insignia «implementado» de cada sistema, y «Flujos del Mercado»
  (traer un flujo con sus sistemas). `flujos-guardados publicar` y `traer` (servidor 1.1.0).

## 1.5.29

El Taller, rehecho como una ruta guiada para construir sistemas de gobernanza. La pantalla anterior apilaba cuatro
bandas (origen, ciclo, una acción suelta y la barra de salida) antes de llegar al sistema, repetía «Taller» y «Nuevo»,
enseñaba botones de salida desactivados y no decía qué hacer a continuación.

- Inicio del Taller: «Cuéntale a uxyn qué deben seguir tus agentes» con la caja de la idea a la vista, y al lado
  «Subir tu material» y «Empezar desde cero» (la especificación JSON queda como enlace). Debajo, los cinco pasos de un
  sistema y «Continúa con un sistema» con su estado (a medias, listo para entregar, en uso, en el Mercado).
- Sistema abierto: cabecera con el título, dónde está y «Sistemas» para cambiar de uno a otro; la ruta Propósito →
  Reglas → Flujo y piezas → Probar → Entregar, con los huecos de cada paso; «Ahora» con una sola acción (ir al paso,
  ir al primer hueco, revisar los cambios de uxyn, abrir el simulador o entregar).
- Cada paso explica qué se decide en él y lista sus archivos con los huecos y su papel (LIMITES.md: las reglas duras;
  PERMISOS.md: qué queda para la persona…). «Rellenar» abre el archivo en el hueco; «Que uxyn complete este paso» le
  pide a uxyn solo ese paso. Propósito usa el formulario de lo básico; Reglas y Flujo y piezas, el editor; Probar,
  la validación y el simulador; Entregar, instalar, la web, el .zip, el Mercado y la versión.
- Abrir un archivo desde cualquier sitio (la guía, «Por revisar» o un error) lleva al paso que lo trabaja.
- uxyn queda abierto al lado por defecto (se pliega y se recuerda); sus cambios siguen en «Por revisar», arriba del
  paso. En móvil la ruta se desplaza en horizontal.

## 1.5.28

Ajustes de uxyn 2 vistos al probar el panel contra la web en producción (backend 1.0.12).

- Tarjeta de cambios: en la columna estrecha del chat las rutas salían cortadas («prom…»); ahora se ven enteras
  (partidas donde haga falta) y debajo el tipo y las líneas +/−.
- «Empezar con uxyn» sin IA: un aviso corto que solo ofrece lo que sirve al crear (la clave en Cuenta → IA y
  conexiones) y recuerda «Crear desde cero» o subir material; los modelos locales y suscripciones se siguen
  explicando en el chat del sistema, donde sí se pueden elegir.

## 1.5.27

uxyn 2 en el panel: las mismas capacidades y la misma experiencia que en la web (contrato compartido
`contrato-uxyn.json`, versión 2, con copia idéntica en el backend, la web y el kit).

- Turno en vivo: el kit pide `POST v1/me/agente/turno/stream` (SSE) y guarda en memoria la fase y los pasos que
  llegan, así «Trabajando en tu sistema» se actualiza sin preguntar al servidor cada 900 ms. Si el servidor no
  ofrece el stream (404/405 u otra respuesta) se vuelve al turno clásico con sondeo el resto de la sesión del panel;
  sin conexión se reintenta la próxima vez; si se agota el tiempo no se repite el turno (no se duplica).
- Errores públicos de uxyn: `SIN_IA`, `LIMITE`, `PROVEEDOR`, `SOLICITUD` e `INTERNO` llegan a la interfaz como
  `uxyn_sin_ia` (acción `configurar_ia`) y `uxyn_*` (acción `reintentar`), documentados en el README.
- Sin IA configurada: el chat y «Empezar con uxyn» lo dicen antes de escribir (GET info → `ia.disponible`), con las
  opciones concretas (clave en Cuenta → IA y conexiones, modelo local o suscripción); sin botón «Reintentar» inútil.
- Tarjeta de cambios en cada respuesta que deja una propuesta: archivos nuevos, cambiados o borrados con +/− líneas,
  totales y «Revisar y aceptar», que lleva a «Por revisar» (nada se escribe sin aceptarlo).
- «Qué puede hacer uxyn» (capacidades del servidor) bajo el saludo y botón «Completar el sistema» con el mismo pedido
  que la web: núcleo y después todo el esqueleto, como sugerencia.
- El servidor (backend 1.0.12) da a uxyn el contexto de todos los archivos del sistema y del esqueleto completo,
  lectura de varios archivos de una vez (`leer_archivos`) y crea el esqueleto completo, no solo el núcleo.

## 1.5.26

Taller y Mis sistemas con una sola lista, esqueleto completo en todos los caminos de creación, importación que no
descarta nada, editor con todos los archivos y un panel con los colores de la web.

- Colores: la capa semántica del panel se reconstruye solo a partir de los primitivos de la web
  (`uxyngraphar-frontend/src/common/theme/palette.ts`): fondo `ink`, texto `edge`, bordes `edge` al 12/20/34 %,
  botón principal dorado `brand` con texto `on-brand`, anillo de foco naranja `tone`, estados desde `affirm`,
  `tone` y `signal`. El panel es oscuro siempre, como la web (se quita el tema claro).
- Estética: iconos con tamaño fijo (16–24 px en línea, 36 px en cabeceras de tarjeta; antes podían salir enormes),
  tokens de espaciado, radios, sombras y duraciones, botones primario/secundario/fantasma/peligro que no se estiran,
  foco visible, insignias, pestañas, diálogos y avisos coherentes, estados vacíos con icono, esqueletos de carga,
  navegación móvil en fila deslizable y `prefers-reduced-motion` global.
- Mis sistemas = Taller: las dos vistas salen de la misma fuente (`/api/mis-sistemas`): sistemas del equipo,
  borradores solo en la web, archivados e instalados propios, cada uno con su insignia de estado; carpetas y arrastre
  por id también para los borradores web; «Traer para editar» y «Restaurar».
- Esqueleto completo al crear (desde cero, zip, archivos, carpeta o especificación): núcleo, `prompts/` y `config/`
  con contenido de arranque, proceso por fases, skills, herramientas, plantillas, referencia, ejemplos, pruebas e
  historial de cambios.
- Importar sin perder nada: nuevo asistente «Nuevo sistema de gobernanza» (Desde cero / Subir zip o archivos / Con
  uxyn / Desde especificación) con arrastrar y soltar archivos o carpetas, vista previa y un resumen de lo colocado,
  fusionado, conservado tal cual y añadido desde la base. Los archivos reconocibles van a su sitio (`docs/` →
  `referencia/`, `templates/` → `plantillas/`, sueltos `.json/.yaml` → `config/`…), las configuraciones JSON se
  fusionan con las de la base (tus valores mandan) y lo desconocido se conserva y se declara en `extensiones`.
  También por CLI: `uxyngraphar importar ORIGEN… [--id --titulo --familia --comprobar --json]`.
- Editor: muestra todos los archivos, en cualquier carpeta y con cualquier extensión; binarios e imágenes en vista
  previa de solo lectura. Los borradores que solo están en la web enseñan su árbol completo antes de traerlos.
- Arreglado: un binario en el sistema hacía fallar «Guardar en la web» entero; «Traer» borraba binarios locales que
  la web no guarda; abrir un binario en el editor daba error; la página «Nuevo» solo enseñaba los archivos del núcleo.
- Arreglado: Proyectos ya no se queda en «sin sesión» si la sesión caducó (las versiones remotas son un extra).

## 1.5.25

Arreglos encontrados probando el kit como usuario nuevo tras una actualización.

- Arreglado: una pestaña del panel abierta desde antes de actualizar (o de volver a abrir el panel) se quedaba en
  «Cargando sistemas…» sin decir nada. Ahora el latido de la pestaña distingue tres casos y lo dice con claridad:
  el panel se cerró o se está reiniciando, el panel se reinició con otro permiso («esta pestaña quedó con un permiso
  viejo») o se instaló una versión nueva mientras este panel seguía abierto (con un botón «Reiniciar el panel con la
  X»). La pestaña sigue latiendo y se reconecta sola en cuanto el panel vuelve o se abre de nuevo (la pestaña nueva
  deja un permiso que vale también para las antiguas); si el proceso cambió de versión, recarga con el código nuevo.
- En el Taller ninguna zona se queda en «Cargando…» para siempre: si la carga falla lo dice y ofrece «Reintentar».
- `proyectos quitar --todo` de una carpeta que nunca estuvo en la lista termina con «limpiado (no estaba en la
  lista)» en vez de «quitado de la lista».
- «Mejorar con uxyn» (y Mejorar, Revisar y el chat) sin ninguna IA configurada explica qué hacer en lugar de un
  error suelto: dónde añadir una clave (web › Cuenta › IA y conexiones), qué modelos locales admite el kit sin clave
  (Ollama y LM Studio) y qué suscripciones con su CLI oficial (Claude Code, Codex, GitHub Copilot CLI y Qwen Code).
  La CLI añade la misma ayuda al error.

## 1.5.24

Arreglos encontrados probando el kit con una cuenta real (borradores del Creador web).

- Arreglado: `creador subir --conservar local` (y «Conservar lo de este equipo» en el panel) decía «subido a la web
  (revisión 0)» sin haber subido nada, y dejaba este equipo creyendo que estaba al día. El servidor manda la revisión
  del conflicto dentro de `details` y el kit la buscaba en la raíz, así que reintentaba con la revisión 0 y tomaba el
  segundo rechazo por un éxito. Ahora lee la revisión donde viene, si la web vuelve a cambiar entre medias lo dice
  como conflicto y nunca da por subido algo que el servidor no confirmó. El aviso de conflicto también enseña la
  revisión real de la web (antes «revisión 0»).
- `creador borradores` avisa cuando la web va por delante de lo que hay en este equipo («con la revisión N: la web
  tiene cambios», y el comando para traerlos).
- `archivar` de un borrador que solo está en la web dice «olvidado en el Taller de este equipo» en vez de «sigue en tu
  catálogo y en tus proyectos».

## 1.5.23

- Arreglado (regresión de 1.5.22): `uxyngraphar --version | head -1` y cualquier comando cuya salida se corta antes
  de tiempo ya no terminan con «error: Broken pipe» y una traza; lo que queda por escribir se descarta y el comando
  termina su trabajo. La salida sigue saliendo por líneas, en orden con los errores.

## 1.5.22

Arreglos encontrados al instalar el kit desde cero y probarlo como un usuario nuevo.

- «Quitar todo» de un proyecto ya no deja carpetas vacías: borra `uxyngraphar/trabajo/<id>/` de los sistemas retirados
  si no tiene nada, y `trabajo/`, `sistemas-de-gobernanza/` y `uxyngraphar/` si se quedan vacías. Solo carpetas
  vacías: tus fichas y cualquier archivo o carpeta ajena se quedan donde estaban. El plan lo dice antes («solo carpetas
  vacías») y avisa de que `.claude/settings.json` se borra si solo tenía las reglas de uxyngraphar.
- El resumen ya no dice «quitado de la lista del panel» cuando el proyecto no estaba en la lista.
- La CLI escribe por líneas: con la salida redirigida a un archivo o a otro programa, el plan de
  `proyectos quitar --todo` sale antes del error que pide `--si` (antes salía al revés).
- Las preguntas «[s/N]» de la CLI (`proyectos quitar --todo`, `eliminar`, `reportar`) ya no acaban en una traza
  cuando nadie puede contestar y la entrada parece una terminal (en Windows, la entrada vacía o NUL): paran sin tocar
  nada y dicen que se confirma con `--si`.

## 1.5.21

**«Por revisar» ya no atasca** (urgente), un editor de código para los archivos del Taller, archivar sistemas y
quitar un proyecto eligiendo entre desvincular o quitarlo todo.

- Arreglado: las sugerencias de uxyn que se quedaban «por revisar» sin salida. Causa: si un archivo cambió después de
  la sugerencia (por ejemplo, porque otra sugerencia posterior ya lo había aplicado), el servidor no la aplica
  (HTTP 409) salvo que se pida expresamente; el kit no lo pedía nunca y convertía esa respuesta en un error genérico,
  así que «Aceptar» fallaba siempre. Además, si el sistema solo estaba en la web, el Taller no enseñaba editor y el
  aviso decía que había que decidir «antes de seguir». Ahora cada archivo pendiente dice si ya está aplicado (basta con
  descartarlo) o si cambió después; al aceptar uno desfasado se elige entre «Aceptar igualmente (sobrescribe)»,
  «Aceptar solo los que no chocan» o descartarlos. Hay «Aceptar todo», «Descartar todo» y «Descartar lo ya aplicado»,
  el panel se puede plegar y el texto ya no bloquea.
- Un sistema que solo está en la web enseña «Traer de la web para editar» (copia a tu catálogo; la web no cambia),
  «Mejorar con uxyn» y, si lo eliminaste de este equipo, «Restaurar de la papelera». Al aceptar una sugerencia se trae
  solo y se abre el editor. uxyn ya puede mejorar un borrador que solo está en la web (antes fallaba al intentar
  subir una copia local que no existía).
- Editor de código en «Archivos» del Taller: árbol con carpetas (crear, renombrar o mover y borrar archivos y
  carpetas), pestañas con aviso de cambios sin guardar (también al cerrar la pestaña o la página), resaltado de
  Markdown, JSON, Python, YAML y shell, números de línea, buscar y reemplazar (Ctrl+F, Ctrl+H), Ctrl+S y «Guardar
  todo», sangría con Tab (Esc y Tab para salir), vista previa de Markdown (solo editor, dividido o solo vista
  previa), divisores arrastrables, «Ampliar» a toda la ventana y una versión para el móvil (el árbol se abre con
  «Archivos»). Los errores de validación salen por archivo en el árbol, por línea en el margen y en «Problemas» (un
  clic lleva a la línea). Las sugerencias de uxyn se abren en el editor como diferencias («Abrir en el editor») y se
  pueden llevar al archivo para retocarlas antes de guardar. Hecho en casa, sin dependencias ni CDN (cumple la CSP).
- Archivar en el Taller: menú «…» por sistema con «Archivar» (o «Olvidar en el Taller» para un borrador solo web) y
  «Eliminar…» (a la papelera, con «Deshacer»). Archivar no borra nada: el sistema sigue en el catálogo, en Mis
  sistemas (insignia «archivado» y filtro), en tus proyectos y en la web. «Mostrar archivados» y «Volver al Taller»
  lo deshacen. Se guarda en `archivados.json` de la carpeta de uxyngraphar. CLI: `archivar <id>…` y
  `desarchivar <id>…`.
- Quitar un proyecto: «Solo desvincular» (sale de la lista y de sus grupos; un grupo que se queda con un solo proyecto
  se borra) o «Quitar todo», que además retira sistemas, `INDICE.md`, `FLUJO.json`, el bloque de AGENTES.md/AGENTS.md/
  CLAUDE.md, las protecciones, la integración y las conexiones de los agentes. Antes se ve la lista exacta y hay una
  segunda confirmación. Los archivos de sistemas que modificaste se copian a `respaldos/quitados/`, lo que no creó
  uxyngraphar (también dentro de la carpeta de sistemas) se queda donde estaba, `uxyngraphar/trabajo/` se conserva y
  una carpeta que ya no existe solo se desvincula. Al terminar, un resumen. CLI:
  `uxyngraphar proyectos quitar RUTA [--todo] [--si]`.
- API del panel: `GET /api/proyectos/plan-quitar`, `POST /api/proyectos/quitar` con `{todo, confirmar}`,
  `GET /api/mis-sistemas/archivados`, `POST /api/mis-sistemas/archivar`, `POST /api/catalogo/archivo/renombrar` y
  `POST /api/catalogo/archivo/borrar`; `/api/agente/decidir` acepta `forzar` y devuelve `{desfasada, rutas}` en vez
  de un error.

## 1.5.20

Nueva sección **Mis sistemas** en el panel para ver, ordenar y gestionar los sistemas que escribes.

- Carpetas (también anidadas) para ordenar tus sistemas: se crean, renombran, mueven y borran
  desde el árbol. Los sistemas se arrastran a una carpeta, entre carpetas, de vuelta a «Sin
  carpeta» o sobre otro sistema para ordenarlos; las carpetas también se arrastran. Sin ratón
  (o en el móvil) está «Mover a…», que además puede crear una carpeta. Borrar una carpeta con
  algo dentro pide confirmación y deja sus sistemas en la raíz: no se borra ningún sistema.
- Las carpetas solo ordenan la vista: se guardan en `.organizacion.json` dentro de la carpeta del
  catálogo y no mueven nada en el disco (la CLI y el Taller siguen encontrando cada sistema). Lo
  que falta en ese archivo sale en la raíz y lo que ya no existe se olvida solo.
- Herramientas de cada sistema: abrir en el Taller, instalar en un proyecto, descargar como zip,
  mover, duplicar, cambiar el nombre y eliminar; estado de validación, búsqueda, filtro por
  familia, orden y selección múltiple para mover o eliminar varios a la vez.
- Eliminar mueve el sistema a la papelera (`<carpeta de uxyngraphar>/papelera/`), con
  «Deshacer» en el aviso. Antes avisa si está instalado en proyectos (que lo conservan) o si
  tiene borrador web o está publicado; nada de eso se toca en el servidor. La vista Papelera
  restaura (a su carpeta y su sitio) o borra para siempre.
- Duplicar crea una copia con otro id y prefijos de fichas nuevos, justo detrás del original;
  las frases de activación propias que chocarían con el original no se copian (te dice cuáles).
- Cambiar el nombre: el título son las palabras del id (nomenclatura), así que con el mismo id
  solo cambian tildes y mayúsculas. Para otro nombre se cambia también el id: se crea el
  sistema con el id nuevo (mismos prefijos y frases) y el anterior va a la papelera. Los
  proyectos donde estaba instalado siguen con el id anterior hasta que instales el nuevo.
- CLI: `mis-sistemas`, `eliminar <id>… [--si]`, `papelera [vaciar [ENTRADA] --si]`,
  `restaurar <entrada|id>`, `duplicar <id> <nuevo-id> --titulo` y
  `renombrar <id> [<nuevo-id>] --titulo`.
- Desinstalar la herramienta cuenta también los sistemas de la papelera como tuyos (no se
  borran sin confirmarlo).

## 1.5.19

Arreglos de crear un sistema desde el panel (Taller), paso a paso, como una persona normal.

- Un sistema nuevo ya no se cita a sí mismo en «Sistemas complementarios» de SISTEMA.md:
  queda un hueco para otro sistema del catálogo (o «ninguno por ahora»).
- «Lo básico»: los ids de los problemas se cortan entre palabras (máx. 40 caracteres) en
  vez de a mitad de palabra, y las palabras de activación se guardan en minúsculas, sin
  tildes ni signos, como pide la nomenclatura (antes «revisar un PR» dejaba el sistema sin
  validar).
- Tras «Instalar en proyecto», la franja del ciclo y la barra de salida muestran el
  proyecto instalado sin recargar la página.

## 1.5.18

- `buscar --familia` con una familia que no existe falla con un error en español que lista
  las familias válidas (antes decía «sin resultados»).
- Una opción desconocida en cualquier subcomando (`buscar --nada`, `creador modelos --x`…)
  muestra el error y el uso de ese subcomando, con la pista `uxyngraphar <comando> --help`,
  en vez de la ayuda general de uxyngraphar. Sale con código 2.
- En Python 3.10 y 3.11 los errores de opciones ya no empiezan con «argument --x:» en inglés.

## 1.5.17

Arreglos de usar la 1.5.16 como una persona normal (contenedor limpio con Python 3.10).

- `crear` ya funciona con ids cuya primera palabra es corta (`mi-sistema` daba «no encuentro
  un prefijo libre»): si hace falta, el prefijo sale de las letras de todo el id. Los prefijos
  que ya se proponían no cambian.
- Si `crear` falla a mitad, no deja una carpeta a medias en el catálogo (antes el reintento
  decía «ya existe» y el sistema quedaba incoherente).
- `buscar` con red guarda también el índice, así que `buscar` e `info` funcionan sin red
  como dice la ayuda. Sin red y sin índice guardado, el error explica por qué.
- `nomenclatura` y `deshacer --lista` dicen cuando no hay nada pendiente; `desinstalar`
  habla en singular cuando solo hay un sistema tuyo.

## 1.5.16

Arreglos del informe de QA de la 1.5.15.

- **Tus sistemas ya no se pierden:** `crear`, `generar desde --aplicar` y el Taller
  escriben en `~/.uxyngraphar/catalogo/` (o `UXYNGRAPHAR_CATALOGO` / `catalogo_local`),
  fuera de `versiones/`. Reparar, actualizar, cambiar de versión y podar versiones ya no
  los borran; los que quedaban dentro de `versiones/` se mueven solos (si un id choca,
  se queda la versión más alta y la otra va a `respaldos/catalogo/`). `desinstalar` de
  la herramienta los lista y pide `--con-catalogo` (en el panel, una casilla).
- `--help` nunca ejecuta nada (`autoactualizar --help` ya no actualiza) y las opciones
  desconocidas se rechazan en español; toda la ayuda de argparse está en español.
- `estado`, `verificar` e `instalar` con un `--repo` que no existe fallan con un mensaje
  claro (y `instalar` no crea la carpeta).
- **Conexiones:** Codex ya no se da por instalado por la carpeta que creamos nosotros, no
  queda un `config.toml` vacío al desconectar y Claude Code de Claude Desktop se detecta.
  Desinstalar un proyecto retira sus conexiones (MCP, instrucciones, bloque global de
  Codex) y la comprobación final dice la verdad.
- `accesos` con un tipo mal escrito ya no borra los accesos existentes.
- `construir`/`empaquetar` sin ids, `andamiar` sin variantes y `creador validar` con un
  borrador inválido ya no callan ni salen con 0.
- `reparar --proyectos` ya no dice «todo estaba bien» después de reconstruir algo.
- **Panel:** sin desbordes en móvil (390 px); Inicio no pide borradores ni propuestas sin
  sesión; errores JSON en español con 401/402/403/404/405 en vez de 400 o páginas HTML.
- Se cierran las respuestas de error HTTP (sin ResourceWarning en Python 3.15).
- Mensajes cuando no hay proyectos, grupos o flujos guardados; errores del sistema y de
  JSON en español, sin «[Errno 2]» ni «Expecting property name».
- Menores: el instalador pide Python 3.10 también en macOS; `version <id> parche` añade
  la entrada al CHANGELOG del sistema (`--nota`); `proyectos agregar` avisa si la ruta ya
  estaba; `deshacer --lista` ya no guarda respaldos de cambios fallidos o sin cambios.

## 1.5.15

- **Creador:** encuentra Claude Code aunque solo tengas Claude Desktop (lo instala en
  su carpeta, fuera del PATH); antes `creador modelos` decía que no había CLI mientras
  `conexiones ver` lo daba por detectado.
- `catalogo` y `validar` avisan cuando el catálogo local está vacío en vez de no
  imprimir nada; `validar <id>` con un id que no existe lo dice y sale con 1.
- `uxyngraphar conexiones` sin acción muestra el resumen (`ver`) en vez de un error de
  argparse en inglés.

## 1.5.14

- **Simulador:** con «uxyn (tu cuenta)» ya no envía un proveedor inválido; usa la IA de la cuenta.
- Historial del chat simple separado por modo; «Nueva» limpia de verdad y se reanuda
  la última conversación (como la web).
- El editor ya no pisa los cambios sin guardar cuando uxyn termina o se acepta una
  sugerencia; aviso al cambiar de archivo, Ctrl+S, «Siguiente hueco»; «Archivo nuevo»
  lo crea al momento.
- «Publicar» solo marca el sistema como publicado si se publicó de verdad.
- Carril: el hueco se describe con archivo y línea, sin las llaves; «Siguiente en el
  ciclo» solo cuando nada lo bloquea.
- Sin sesión no se consulta a la web (borradores/propuestas): menos esperas.
- Se quita «Traer y Subir» (bajaba la versión web y la volvía a subir).

## 1.5.13

- **Taller más usable:** al abrir un sistema ya no te deja 8+ s en «Cargando…»:
  pinta el marco al instante y rellena lista/editor/franjas en segundo plano.
- Menos llamadas repetidas (caché de catálogo, borradores y proyectos en la vista);
  el editor no dispara un repintado en cascada al montarse.
- El editor abre por defecto `sistema.json` (luego README / SISTEMA), no el primer
  archivo alfabético (`CHANGELOG.md`).
- «Por revisar» y el chat de uxyn se montan aparte: el cajón uxyn puede seguir
  cerrado sin bloquear la carga; «Traer y Subir» cuando el sistema está en web y equipo.
- Latidos fallidos ya no muestran «El panel se cerró»; al arrancar se oculta ese aviso.
- Se cuentan solo propuestas realmente pendientes (`PENDING`).
- Carril: «Validar» vuelve a validar (no llama a uxyn); «Que uxyn complete» abre el
  archivo del hueco si lo hay. Inicio y Taller comparten la misma regla de `valido`.
- Tras Subir se refresca la lista; sync usa `slug` de la API; textos apuntan a «Cuenta»;
  `#/logs` redirige a Cuenta → Logs; el nombre del borrador se guarda en el origen.

## 1.5.12

- **Taller de sistemas (ADR 0015):** el panel deja el Creador chat-first.
  Navegación: Inicio · Taller · Proyectos · Mercado · Cuenta. En un sistema:
  franja Origen, carril de ciclo (Borrador → En equipo → En proyecto → Mercado),
  barra de salida siempre visible (Descargar .zip, Traer y Subir a la vez si
  aplica, Instalar, Publicar), archivos/editor por defecto y uxyn en cajón.
  «Abrir salida» / «Publicar» del carril enfoca la barra real. Logs en Cuenta.
  Contrato `creador-estado` añade `enEquipo`, `enProyecto`, `publicado` y
  `origen`. El badge **mercado** usa `version_publicada` del borrador web
  (no solo el publicar de esta sesión).

## 1.5.11

- **Creador (panel):** «Que uxyn complete» arma el mensaje según pendientes:
  si no hay marcadores `{{…}}` pero sí errores (p. ej. `permisos.acciones`),
  pide corregir esos errores en lugar de repetir «sustituye marcadores».

## 1.5.10

- **Permisos:** el error de `permisos.acciones.*` aclara que hace falta
  `scripts/….py [subcomando]` (o `[]`); el texto libre no vale y va en
  LIMITES.md / PERMISOS.md «Por qué».

## 1.5.9

- **Creador:** tras crear/traer un sistema, el editor ya no dice «No encuentro» por
  un catálogo en caché vacío. Recarga el catálogo (con un reintento corto) antes de abrir.

## 1.5.8

- **Logs del panel:** cajón en el Creador y sección «Logs» en el menú. Registra API, turnos
  uxyn, traer borrador, progreso y errores (sin secretos). `GET /api/registros` mezcla eventos
  del servidor.

## 1.5.7

- **Creador, menos ruido:** al crear no se repite el mismo texto en cabecera, carril, editor y
  uxyn. Carril solo cuando ya hay sistema o uxyn está trabajando; una sola caja para la idea.

## 1.5.6

- **Puesto asistido:** carril de estado (qué falta / qué revisar / siguiente paso), Editor a la
  izquierda y uxyn a la derecha también al crear. Idea o zip van por uxyn; plantilla paso a paso
  queda en Avanzado. Lista y sync como cajón.

## 1.5.5

- **Creador más claro:** zonas Lista | Editor | uxyn; al crear, hero centrado sin chat lateral.
- **«Por revisar»:** las sugerencias de uxyn viven en un bloque fijo encima del chat (aceptar,
  corregir o rechazar), no perdidas en el hilo. Borradores web van colapsados.
- Tipografía de «Por revisar» solo con tokens (`--font-size-md`), sin fallbacks en CSS.

## 1.5.4

- Intento de release cancelado: falló la prueba de tipografía del panel (fallback en CSS).

## 1.5.3

- **uxyn**, el agente propio del Creador: chats guardados (listar y reanudar conversaciones), foco en
  sistemas de gobernanza para agentes de IA, y corrección en vivo de sugerencias antes de aceptarlas.
  Nuevas rutas `GET /api/agente/conversaciones` y `POST /api/agente/corregir`.

## 1.5.2

- **Agente del Creador:** si el servidor aún no admite el campo `progreso` (pasos en vivo), el panel
  reintenta el turno sin él en lugar de fallar con «property progreso should not exist».

## 1.5.1

- **Creador, flujo claro crear vs editar:** sin sistema abierto solo ves «Crea un sistema» (sin chat a la
  derecha). Con sistema abierto: editor + un chat con modos Asistente | Simulador (IA bajo Avanzado).
  «Guardar borrador en la web» y «Publicar en el Mercado» van separados a propósito.

## 1.5.0

- **Creador, más simple y moderno (igual que la web):** una sola caja para hablar con el agente con
  el texto, los adjuntos y el botón; ejemplos cortos; el chat del agente usa la misma caja.
- **Adjuntar un .zip:** se abre en el navegador y se toman sus archivos de texto, primero documentos
  y configuración, hasta 80 archivos y 200 mil caracteres. Se explica qué se tomó y qué se omitió
  (binarios, .git, node_modules, lo que no cabe).
- **Asistente del Creador inspirado en Deo (uxconstructar):** mientras trabaja se ven sus pasos en
  vivo («Leyendo SISTEMA.md», «Proponiendo cambios…»); respuestas con formato (negritas, listas,
  código), hora y copiar; los pasos hechos bajo cada respuesta y «Reintentar» si un turno falla.
  Nueva ruta `GET /api/agente/progreso`; `POST /api/agente/turno` acepta `progreso`.

## 1.4.0

- **Creador de sistemas, igual que en la web:** «Crea un sistema con el agente» (cuenta tu idea y/o
  adjunta archivos o una carpeta de texto) en la zona central y como primera opción de «Crear
  sistema». El agente crea el borrador y deja el contenido como propuestas; el panel lo trae a este
  equipo y lo abre con su conversación y las propuestas pendientes.
- El chat del agente admite archivos adjuntos (30 archivos, 200 mil caracteres; se ignoran `.git`,
  `node_modules` y binarios). Nueva ruta `GET /api/agente/conversacion`.
- **Tus suscripciones de IA** (ADR 0014): el Creador puede usar Claude Code, Codex, Copilot CLI y
  Qwen Code con la sesión de su CLI en tu equipo (sin leer tokens). Panel › Conexiones las lista con
  riesgo y aviso de términos; nunca se eligen solas. Google AI Pro/Ultra no se ofrece. En Windows se
  lanzan también las CLI instaladas como `.cmd` (p. ej. las de npm).

## 1.3.0

- **Mis proyectos:** carpetas con nombre y color (plegables y reordenables), etiquetas de colores,
  arrastrar y soltar entre carpetas, búsqueda, filtros, orden y vista de tarjetas o lista; se
  recuerdan en el navegador. La organización vive en `organizacion.json` y en `/api/organizacion/*`.
- **Flujos guardados:** sección más visual (plantillas, tarjetas por forma de trabajar, filtros y
  orden), asistente de creación en cuatro pasos, crear desde un proyecto, aplicar a varios repos
  con vista previa, y editor con fichas; estilos en `web/flujos.css`.

## 1.2.2

- El panel, el favicon y los accesos directos usan la PNG oficial de marca (`icono.png`); se elimina el
  `icono.svg` inventado que no coincidía con las logos del sistema.

## 1.2.1

- Identidad visual renovada desde las logos: paleta «Tres señales» pasa a oro/naranja/verde
  (brújula) y el icono del panel usa la nueva marca.

## 1.2.0

- Se quita el «Modo avanzado»: todas las funciones del panel están siempre visibles.
- Nueva sección **Creador de sistemas** con tres zonas que se pueden ocultar (Mis sistemas, el sistema abierto y el
  agente); lo que se ve se recuerda en el navegador. Lo básico de `sistema.json` se edita con un formulario, las piezas
  con interruptores, «Lo que falta» lleva a cada marcador por rellenar, y la tarjeta de borradores de la web vive aquí
  (antes en «Herramienta y ajustes»). El Catálogo queda para buscar e instalar; su botón «Editar» abre el Creador.
- El chat del Creador habla con el **Asistente del Creador** del servidor (protocolo creacion-agente): lee y valida
  el sistema, crea borradores y deja **propuestas** que se aceptan o rechazan archivo por archivo en el propio chat;
  al aceptar se traen a este equipo. Sigue disponible el chat simple con tu clave o con Ollama / LM Studio.
- Nueva sección **Conexiones**: detecta Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Grok y Copilot y los conecta
  a tus proyectos (instrucciones de uxyngraphar en su archivo y uxyngraphar como servidor MCP). También por terminal:
  `uxyngraphar conexiones ver|conectar|desconectar`.
- `uxyngraphar mcp`: servidor MCP de solo lectura (buscar sistemas, ver los del proyecto, leerlos y ver el flujo).
- GEMINI.md se mantiene con el bloque de uxyngraphar si el proyecto lo tiene.

## 1.1.2

- El panel (Catálogo › modo avanzado) permite **Publicar en el Mercado**: misma ruta que
  `uxyngraphar publicar` (empaquetar + subir), con simulación, confirmación de tamaño/sha256 y opción
  de alinear el campo `editor` de `sistema.json` con el `@usuario` de la sesión antes de publicar.
- Distinto de «Subir al Creador web» (borrador sincronizado).

## 1.1.1

- Al instalar o actualizar, si ya hay una carpeta local con el mismo número de versión pero otra huella que la
  release publicada (p. ej. tras reiniciar tags), se descarga de nuevo en lugar de reutilizar la copia vieja.
- El panel y `autoactualizar` detectan ese desfase (mismo X.Y.Z, otro zip) como actualización pendiente.

## 1.1.0

- `iniciar-sesion`, `sesion` y `cerrar-sesion`: el equipo se conecta con tu cuenta aprobando un código en la web
  (ADR 0011). En CI, `UXYNGRAPHAR_TOKEN`.
- `sincronizar` y tarjeta «Mi biblioteca» del panel: lo obtenido, comprado y propio se descarga a la caché al iniciar
  sesión, al abrir el panel o a petición, comprobando cada sha256 (ADR 0012). Lo de pago y lo privado se resuelven
  desde la biblioteca guardada, también sin red. Nada se aplica solo: cada proyecto muestra «Actualización disponible».
- Los sistemas de pago sin comprar responden con un mensaje claro (`DePago`, código `de_pago` en el panel).
- Creador (ADR 0013): `creador borradores|bajar|subir` lleva los borradores del Creador web al catálogo local y vuelve,
  con control por revisión (ante un conflicto se ven las diferencias y se elige qué conservar). `creador modelos` lista
  los modelos locales (Ollama, LM Studio). El editor del catálogo del panel añade el asistente de IA (mejorar un archivo
  con vista de diferencias, revisar el sistema, chat y simulador) con un modelo local o la clave de IA de tu cuenta.
- `creador validar|nuevo|desde-spec|empaquetar --dir`: puente que usa el servidor para validar, crear y empaquetar
  borradores con las mismas reglas que el kit.
- `reportar <[editor/]id> --tipo problema|mejora|duda --texto "…"` y botón «Reportar al autor» en cada sistema
  instalado del panel: cuenta al autor qué falla o qué falta. Siempre se ve antes lo que sale del equipo (tipo, texto,
  sistema y versión, versión del kit, sistema operativo y Python; nunca rutas ni código). Necesita sesión y que el
  sistema esté en tu biblioteca; el autor lo recibe en «Sugerencias» del Creador.

## 1.0.0

Primera versión pública de uxyngraphar: herramienta 1.0.0, protocolo de sistemas v1 (`manifiesto_formato` 1,
`FLUJO.json` formato 1).

### Protocolo

- Cada sistema de gobernanza es una carpeta con `sistema.json`, `README.md`, `DESCRIPCION.md`, `MEMORIAS.md`,
  `LIMITES.md` y `PERMISOS.md` en su núcleo, más piezas estándar opcionales (`proceso`, `skills`, `plantillas`,
  `referencia`, `ejemplos`, `pruebas`, `CHANGELOG.md`…) y `scripts/comun/` de `_base`.
- `permisos` `{rutas: {protegidas, fuera_de_ia}, acciones: {agente, solo_persona}}`: `PERMISOS.md` lleva un bloque
  generado y `scripts/comun/uxyn_permisos.py` ofrece `exigir(sistema, accion)` a los scripts propios.
- Memorias del proyecto en `uxyngraphar/trabajo/<id>/memorias/MEM-AAAAMMDD-slug.md`: el agente solo las propone; la
  persona las aprueba o archiva (`scripts/comun/memorias.py`).
- `INTEGRIDAD.json` (sha256 de cada archivo) para detectar sistemas alterados; `FLUJO.json` decide qué sistemas se
  aplican (`manual`, `leer_por_defecto`, `trabajar_con`, `secuencia`).
- Nombres, status y prefijos según `NOMENCLATURA.md` y `nomenclatura.json`.

### Herramienta

- Un solo comando, `uxyngraphar`: catálogo (`crear`, `generar`, `validar`, `pieza`, `version`, `construir`,
  `empaquetar`), servidor (`buscar`, `info`, `traer`, `publicar`), proyectos (`instalar`, `actualizar`, `quitar`,
  `estado`, `verificar`, `indice`, `andamiar`, `flujo`, `grupos`, `deshacer`, `retirar`) y equipo (`proyectos`,
  `flujos-guardados`, `accesos`, `diagnostico`, `reparar`, `desinstalar`).
- Cada cambio en un proyecto es una transacción con respaldo: un fallo o un corte deja el proyecto como estaba y
  `deshacer` vuelve a antes del último cambio.
- Bloque «uxyngraphar» en `AGENTES.md`/`AGENTS.md`/`CLAUDE.md`, `INDICE.md` y protecciones (`.claude/settings.json`,
  `.cursorignore`, `.geminiignore`, `.aiexclude`) regenerados por el motor.
- Workflow de CI y gancho pre-commit opcionales para `verificar`.

### Servidor de sistemas de gobernanza

- El instalador llega vacío: los sistemas se buscan, se traen y se publican en el servidor como artefactos zip
  reproducibles (`<id>-<version>.zip`), con caché local para trabajar sin red.

### Panel

- Panel web local (solo `127.0.0.1`, código de un solo uso, CSP): inicio con avisos, proyectos, catálogo, flujos
  guardados, grupos, memorias, revisión y herramienta; se cierra solo cuando no queda ninguna pestaña.

### Instalación

- Instalador de una línea para Linux, macOS y Windows con huella `SHA256SUMS` y atestación de procedencia; versiones
  guardadas, vuelta a la anterior, reparación y desinstalación por alcance.
