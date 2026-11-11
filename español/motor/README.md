# uxyngraphar — kit (español)

Catálogo de **sistemas de gobernanza** para repos trabajados por personas y agentes de IA, y la herramienta que los instala.
Cada sistema es un **entorno de trabajo completo** para un conjunto acotado de problemas: qué resuelve y qué no, sus límites,
su proceso por fases, sus skills, sus herramientas, su andamiaje y sus ejemplos, todo dentro de su carpeta.

```
español/
  motor/                  todo lo que instala, actualiza, configura y desinstala uxyngraphar
    uxyngraphar.py        el único comando: panel, catálogo, instalar/actualizar/quitar, flujo, andamiar…
    VERSION               versión de la herramienta
    README.md  ESPECIFICACION.md  NOMENCLATURA.md  GUIA-DE-SISTEMAS.md  GENERADOR.md  GUIA-PARA-AGENTES.md  CHANGELOG.md
    cli.py catalogo.py generador.py especificacion.py piezas.py entrada.py andamiaje.py nomenclatura.py repo.py generar.py …
    panel.py rutas_panel.py proyectos.py flujos_guardados.py herramienta.py casa.py   servidor y API del panel
    remoto.py fuentes.py artefacto.py   servidor de sistemas: buscar, traer (con caché), publicar; zip de cada sistema
    web/                  la interfaz del panel (HTML, CSS y JS sin compilación)
    distribucion/         instalador de una línea, accesos directos y publicación de releases
    pruebas/              pruebas de todo lo anterior
  sistemas-de-gobernanza/  el catálogo fuente: un sistema por carpeta (en el instalador solo va _base; los sistemas
                           se publican en el servidor y se traen de ahí)
    _base/                el protocolo: núcleo (sistema.json, README.md, SISTEMA.md), scripts/comun/ y piezas/<pieza>/ (semillas; no es un sistema)
```

## De dónde salen los sistemas

El instalador llega vacío. Los sistemas viven en el servidor (`/v1/sistemas`, ADR 0007) y se traen al equipo:

```
uxyngraphar buscar secretos          # busca en el servidor (sin red, en el último índice guardado)
uxyngraphar info secretos-y-credenciales
uxyngraphar instalar secretos-y-credenciales --repo .   # lo trae si hace falta y lo instala
uxyngraphar cache                    # lo traído: ~/.uxyngraphar/sistemas-de-gobernanza/<editor>/<id>/<version>/
```

Quien escribe sistemas trabaja con un catálogo local (este `sistemas-de-gobernanza/`, `UXYNGRAPHAR_CATALOGO` o
`catalogo_local` en `casa.json`) y publica con `uxyngraphar sesion guardar <token>` + `uxyngraphar publicar <id>` (o
`--todos`, `--simular`). Si un id está en local y en el servidor, se instala la versión más alta; a igual, la local.
`UXYNGRAPHAR_SIN_RED=1` trabaja solo en local.

## El protocolo de sistemas

`sistemas-de-gobernanza/_base/` rige **la estructura**, no el contenido (contrato completo en [`ESPECIFICACION.md`](ESPECIFICACION.md) §2;
criterio de diseño en [`GUIA-DE-SISTEMAS.md`](GUIA-DE-SISTEMAS.md)):

- **Núcleo obligatorio:** `sistema.json` (con `alcance`: problemas que cubre y lo que deriva a otros sistemas), `README.md`
  (bloque de entrada generado + texto libre), `SISTEMA.md` (la descripción del sistema), `MEMORIAS.md` (qué conviene
  recordar del proyecto), `LIMITES.md` (reglas duras y cuándo detenerse) y `PERMISOS.md` (qué hace el agente solo y qué
  decide una persona, generado desde `permisos` del manifiesto) más `scripts/comun/` (con `memorias.py` y `uxyn_permisos.py`).
- **Memorias del proyecto:** viven en `uxyngraphar/trabajo/<id>/memorias/`. El agente las lee siempre al activar el
  sistema y solo propone nuevas; la persona las aprueba o archiva (`memorias.py aprobar|archivar --humano` o la pestaña
  «Memorias» del panel). Contrato en [`ESPECIFICACION.md`](ESPECIFICACION.md) §2.3.
- **Límites y permisos:** el agente no ejecuta las acciones de «Solo una persona» ni toca las rutas protegidas o fuera de
  la IA; los scripts propios lo imponen con `uxyn_permisos.exigir`. Contrato en [`ESPECIFICACION.md`](ESPECIFICACION.md) §2.4.
- **Piezas estándar opcionales**, con forma fija y declaradas en `piezas`: `proceso` (`proceso/<fase>.md`),
  `skills` (`skills/<nombre>/SKILL.md`), `componentes`, `herramientas`, `andamiaje`, `plantillas`, `referencia`, `ejemplos`,
  `pruebas` y `cambios` (`CHANGELOG.md`).
- **Extensiones libres**, declaradas en `extensiones` con su propósito: lo que no encaje en una pieza.

Solo es error lo que rompe la estructura (núcleo, piezas declaradas frente a presentes, forma de cada pieza, entradas sin declarar);
lo demás son avisos (más de 5 problemas, problemas sin cubrir, piezas recomendadas para la familia). Agregar, quitar o actualizar
una pieza es un comando; quitar un sistema es borrar su carpeta.

Cada sistema lleva todo lo que necesita para funcionar y verificarse: copiar su carpeta a otro `uxyngraphar/sistemas-de-gobernanza/` basta.
Las skills viven solo dentro del sistema (el agente las lee desde ahí; nada se copia a `.cursor/` ni `.claude/`).
Los nombres siguen [`NOMENCLATURA.md`](NOMENCLATURA.md); `validar` y `crear` la comprueban.
El sistema de referencia es `arquitectura-monolitica-por-capas` (en el servidor: `uxyngraphar info arquitectura-monolitica-por-capas`), que usa todas las piezas.

## En un repo

```
mi-repo/
  AGENTES.md                       bloque generado: cuándo mirar los sistemas
  uxyngraphar/
    INDICE.md                      sistemas instalados, frases de activación y problemas que cubren (generado)
    FLUJO.json                     cómo trabaja el agente (lo decide una persona)
    sistemas-de-gobernanza/                      sistemas instalados (inmutables)
      arquitectura-monolitica-por-capas/  README.md  SISTEMA.md  MEMORIAS.md  LIMITES.md  PERMISOS.md  proceso/  skills/  …  INTEGRIDAD.json
    trabajo/                       el trabajo del proyecto
      decisiones-de-arquitectura/completadas/ADR-20261105-orm.md
      decisiones-de-arquitectura/memorias/MEM-20261105-orm-sin-migraciones.md
      instrucciones-aprobadas/instrucciones/pendientes/INS-20261105-landing.md
```

Ningún sistema actúa solo: el agente los usa cuando el pedido dice «usa el sistema X» / «sigue el protocolo X» o cuando
`FLUJO.json` lo indica. Entonces sigue el bloque de entrada del README del sistema: integridad, `SISTEMA.md` (si el pedido
está fuera de alcance, deriva), las memorias (`MEMORIAS.md` y las vigentes del proyecto), `LIMITES.md` y `PERMISOS.md`, las fases de `proceso/` en orden y las skills que cada fase cita.

## El panel

`uxyngraphar` (o su acceso directo) abre el panel en el navegador. Todo se gestiona desde ahí, sin comandos:

- **Inicio**: estado de todos tus proyectos, avisos de lo que pide atención (versión nueva, cambios a
  medias, actualizaciones, fichas con status antiguos) y lo más habitual a un clic.
- **Mis proyectos**: añade carpetas con el explorador (o deja que busque los repos dentro de una carpeta). En cada proyecto:
  instalar, actualizar, reparar o quitar sistemas; las memorias del proyecto (aprobar o archivar las que propone el
  asistente y crear las tuyas); el flujo del asistente con su diagrama; la revisión; quitar uxyngraphar.
  «Deshacer…» vuelve a antes del último cambio. En la revisión se puede añadir
  (o quitar) una comprobación automática en CI o antes de cada commit. Los **grupos** reúnen los repos de un mismo sistema
  para actualizarlos y verificarlos juntos (con la comparación de contratos entre ellos) y ver su matriz repo × sistema.
- **Flujos guardados**: combinaciones de sistemas y forma de trabajar que se aplican a uno o varios proyectos con un clic.
  Se guardan en `flujos/` de la carpeta de uxyngraphar (sobreviven a las actualizaciones) y se exportan o importan como `.json`.
- **Catálogo**: busca por el problema que quieres resolver e instala en varios proyectos a la vez. «Modo avanzado» muestra el
  editor de sistemas.
- **Herramienta y ajustes**: actualizar uxyngraphar (el panel se reinicia solo y ofrece actualizar todos tus proyectos),
  volver a una versión guardada, accesos directos, el historial de acciones y desinstalar.

Solo escucha en `127.0.0.1`. La URL que se abre lleva un código de un solo uso (vale 60 s) que la pestaña canjea por una
cookie `HttpOnly`; rechaza otro `Host` u `Origin` y envía CSP en todas las respuestas. Hay un panel por equipo: abrirlo otra vez reabre el mismo. Corre en su
propio proceso, así que puedes cerrar la terminal desde la que lo abriste. Se cierra con «Cerrar el panel», con
`uxyngraphar panel --cerrar` o solo cuando no queda ninguna pestaña abierta (`panel --mantener` lo evita), y libera el puerto.
`panel --primer-plano` lo deja atado a la terminal (Ctrl+C lo cierra); si no arranca, el motivo queda en `panel.log` de la
carpeta de uxyngraphar.

El instalador pregunta si quieres accesos directos (menú o Inicio, escritorio, barra de tareas o dock); también se cambian
desde el panel o con `uxyngraphar accesos menu,escritorio,barra`.

### Errores de la API

Todo error responde `{"error": {"codigo", "mensaje", "accion"}}`; `accion` dice qué puede ofrecer la web.

| Código | Estado | Acción | Cuándo |
|---|---|---|---|
| `campo_obligatorio` | 400 | — | falta un campo del pedido |
| `proyecto_no_registrado` | 400 | `registrar` | se quiere cambiar una carpeta que no está en «Mis proyectos» |
| `falta_confirmacion` | 400 | `confirmar` | acción que borra o mueve trabajo sin `confirmar` |
| `ajustes_claude_invalidos` | 400 | `corregir_ajustes` | `.claude/settings.json` no es JSON válido |
| `sin_permiso` | 400 | — | el sistema no deja leer o escribir |
| `no_encontrado` | 400 | — | no existe lo pedido |
| `ya_existe` | 400 | — | ya existe lo que se quería crear |
| `pedido_invalido` | 400 | — | otro dato del pedido no vale |
| `json_invalido` · `content_length_invalido` | 400 | — | el cuerpo del pedido está mal formado |
| `sin_sesion` · `codigo_caducado` | 403 | `abrir_de_nuevo` | pestaña sin cookie válida, o enlace ya usado o caducado |
| `host_no_permitido` · `origen_no_permitido` | 403 | — | `Host` u `Origin` que no son del panel |
| `ruta_desconocida` | 404 | — | la ruta de la API no existe |
| `proyecto_ocupado` | 409 | `reintentar` | otro proceso está cambiando el proyecto |
| `pedido_demasiado_grande` | 413 | — | cuerpo de más de 1 MiB |
| `error_interno` | 500 | `ver_registro` | fallo no previsto; `detalle` y `registro` dicen dónde mirar |

## Uso

Desde `español/` (instalado, basta `uxyngraphar …`):

```bash
python3 motor/uxyngraphar.py                         # panel en el navegador
python3 motor/uxyngraphar.py catalogo                # sistemas disponibles (con avisos)
python3 motor/uxyngraphar.py validar --completitud   # piezas de cada sistema y recomendadas que faltan
python3 motor/uxyngraphar.py instalar secretos-y-credenciales instrucciones-aprobadas --repo ../mi-app --base instrucciones-aprobadas
python3 motor/uxyngraphar.py andamiar arquitectura-monolitica-por-capas modulo-servidor --nombre orders --repo ../mi-app   # simula; --aplicar crea
python3 motor/uxyngraphar.py flujo --repo ../mi-app --modo leer_por_defecto --leer secretos-y-credenciales
python3 motor/uxyngraphar.py proyectos agregar ../mi-app ../otra-app   # proyectos que gestiona el panel
python3 motor/uxyngraphar.py flujos-guardados guardar "API con revisión" --repo ../mi-app
python3 motor/uxyngraphar.py flujos-guardados aplicar api-con-revision ../otra-app
python3 motor/uxyngraphar.py retirar --repo ../mi-app # quita uxyngraphar del proyecto (conserva el trabajo)
python3 motor/uxyngraphar.py deshacer --repo ../mi-app            # vuelve a antes del último cambio (--lista: los posibles)
python3 motor/uxyngraphar.py nomenclatura migrar --repo ../mi-app # fichas al vocabulario nuevo (simula; --aplicar)
python3 motor/uxyngraphar.py verificar --repo ../mi-app --formato json --trabajos 4
python3 motor/uxyngraphar.py grupos guardar sistema ../api ../web # y: grupos actualizar|verificar|matriz sistema
python3 motor/uxyngraphar.py diagnostico --anonimizar            # informe para entender qué pasa o pegarlo en una incidencia
python3 motor/uxyngraphar.py completado bash >> ~/.bashrc        # autocompletado (también zsh, fish y powershell)
python3 -m unittest discover -s motor/pruebas -t motor/pruebas
```

Crear o cambiar un sistema (o desde la pestaña Catálogo del panel). El generador ([`GENERADOR.md`](GENERADOR.md)) crea un
sistema completo desde una especificación JSON o guía su creación paso a paso; los agentes de IA siguen
[`GUIA-PARA-AGENTES.md`](GUIA-PARA-AGENTES.md):

```bash
python3 motor/uxyngraphar.py generar plantilla --id contratos-de-pago > spec.json   # especificación de partida
python3 motor/uxyngraphar.py generar desde spec.json --aplicar          # sistema completo (sin --aplicar, simula)
python3 motor/uxyngraphar.py generar pendientes contratos-de-pago       # qué falta y la siguiente acción (--json)
python3 motor/uxyngraphar.py crear contratos-de-pago --titulo "Contratos de pago" --familia arquitectura --piezas proceso,skills,cambios
python3 motor/uxyngraphar.py pieza contratos-de-pago agregar ejemplos   # o: quitar <pieza>
python3 motor/uxyngraphar.py indice-sistema contratos-de-pago           # tras editar sistema.json a mano
python3 motor/uxyngraphar.py version contratos-de-pago menor
python3 motor/uxyngraphar.py actualizar --repo ../mi-app
```

Un sistema creado con `crear` no valida hasta rellenar los marcadores `{{…}}` de su núcleo (`SISTEMA.md` y `alcance`);
`generar pendientes` dice dónde están.
