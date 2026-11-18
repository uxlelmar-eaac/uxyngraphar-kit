# Cambios

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
