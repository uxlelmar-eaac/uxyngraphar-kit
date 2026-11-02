# CHANGELOG — uxyngraphar (pack documental)

Evolución versionada del pack. Este archivo **viaja dentro de cada pack**: el repo que lo adopta registra la versión copiada en `00-nucleo/configuracion-proyecto.md` y se actualiza comparando contra el CHANGELOG de la plantilla más reciente.

Formato: una entrada por lote de cambios; origen (plan/EVO/decisión humana) siempre citado.

## [1.2.1] — 2026-11-01

Origen: decisión humana (Uxleleaac, 2026-11-01: los agentes no deben poder destruir ni alterar el núcleo de uxyn en un proyecto real; framework rígido — nadie, ni el humano del proyecto, altera el núcleo). Aplica a **ambos packs**. Parche: sin migraciones.

### Núcleo inviolable (fail-closed)
- Al proteger (`--proteger` / panel / `doctor.py --fix`): manifiesto `.cursor/uxyngraphar-protegido.json`, guardia `.cursor/hooks/uxyngraphar-guardia-nucleo.py`, `.cursor/hooks.json` con `failClosed: true` en `preToolUse` y `beforeShellExecution`, y regla `.cursor/rules/uxyngraphar-nucleo.mdc`.
- Archivos clase N (+ lock) y carpetas `10-guias/`, `scripts/`, `55-automatizaciones/`, `00-nucleo/` (más mecanismos) quedan en solo lectura; no se pueden crear archivos nuevos en zonas N.
- `actualizar-pack.py` / mover / doctor descongelan, escriben y vuelven a congelar; `respaldos.restaurar`, `transaccion.deshacer` y `lock.escribir` respetan el congelado (también en Windows).
- `doctor.py`: deny / Cursor / FS / CODEOWNERS faltantes = **ERROR**; `--fix` regenera capas y reaplica el congelado.
- `controlar.py`: control `nucleo` siempre bloqueante; `niveles.nucleo` ≠ bloqueante es inválido en la config.
- `PROTOCOLO.md` R-20, `REGLAS.md` y `congelamiento.md` alineados al framework rígido.
- Documentación: `00-nucleo/congelamiento.md`, `protecciones.md`, `AGENTES.md`, `control-de-construccion.md`.

## [1.2.0] — 2026-11-01

Origen: decisión humana (uxlelmar, 2026-11-01: «dejar de usar la consola de comandos y que todo se pueda gestionar, configurar, actualizar de forma sencilla, directa y rápida desde el panel visual. Que como tal el único comando que se utilice con la consola de comandos es para abrir el panel.»), ficha EVO-20261101-todo-desde-el-panel; y (Uxleleaac, 2026-10-31) cerrar las instancias que levanta el agente. Aplica a **ambos packs**. Menor: sin cambios en el texto de las reglas R-xx ni migraciones.

### Un solo comando: `uxyngraphar`
- `uxyngraphar` sin nada más abre el panel (con CI, un agente o sin escritorio sigue imprimiendo la ayuda). `uxyngraphar ayuda` lista los comandos, que siguen funcionando igual y se presentan como avanzados.
- **Proyecto → Salud:** el doctor completo y «Arreglar» (`doctor.py --fix`) con copia de los archivos que puede tocar y aviso de lo que cambió.
- **Proyecto → Pendientes:** instrucciones por aprobar, MEJ, EVO, propuestas, ADR y auditorías; se lee la ficha, se ve el cambio exacto y se confirma (como `decisiones.py register` + `apply`), con copia.
- **Proyecto → Copias de seguridad** (ver diferencias, restaurar, borrar caducadas), **Memoria** (buscar, ver, recuperar, purgar), **Protecciones** (ganchos de git y propietario de CODEOWNERS) y **Reglas y fichas** (reglas del equipo, archivar fichas antiguas). Colaborar muestra exactamente qué saldría y permite enviar.
- **Sistema:** versiones guardadas (usar otra o descargarla), añadir o quitar el comando del PATH, limpiar proyectos que ya no existen y una instalación cortada, y desinstalar.
- Tras «Actualizar a X» el panel se reabre solo en la versión nueva (`uxyngraphar panel --fondo`).
- Pestaña «Atajos y comandos»: el único comando, dónde está cada cosa en el panel y, plegados, los comandos para usuarios avanzados, CI y agentes. Las guías y `AGENTES.md` indican a la persona dónde hacerlo en el panel.
- Todo con los mismos resguardos: solo en tu equipo con token, nada cambia sin una persona delante ni sin vista previa, y cada acción usa los scripts de la versión del pack de cada proyecto.

### Protocolo del agente
- `AGENTES.md` y `00-nucleo/agentes-detalle.md`: quien arranque un servidor, un watcher u otra instancia la cierra antes de terminar el turno. Si el puerto ya está en uso, no levanta otra copia.

## [1.1.0] — 2026-11-01

Origen: decisión humana (uxlelmar, 2026-11-01: «Ya no quiero que la carpeta se llame Docs, quiero que sea una carpeta que haga referencia a uxyngraphar» y poder configurar la frase «sigue el protocolo …»; nombre elegido: `uxyngraphar/`). Fichas: EVO-20261101-frases-activacion y EVO-20261101-carpeta-uxyngraphar. Aplica a **ambos packs**. Menor: sin cambios en el texto de las reglas R-xx; una migración automática.

### Frases que activan el protocolo
- Nueva sección `protocolo.alias` en `uxyngraphar.config.json` (por defecto `uxyngraphar`, `uxyn`, `uxynar`): un pedido que termina en «sigue el protocolo <frase>» pide el flujo de `AGENTES.md`. Se edita en el panel (proyecto y plantilla).
- El agente las ve al empezar en la línea «Activación» de `ESTADO.md` (al instalar, al guardar desde el panel, con `decisiones.py estado --escribir` y `doctor.py --fix`; el doctor avisa si está desfasada). `contexto.py --activacion` la imprime.

### Carpeta del pack: `uxyngraphar/`
- Las instalaciones nuevas van a `uxyngraphar/` (o `apps/<app>/uxyngraphar/`). Las anteriores siguen en `docs/` y funcionan igual: actualizar no mueve nada.
- Las herramientas deducen la carpeta si no se indica `--docs` (`scripts/carpeta_pack.py`) y aceptan rutas con cualquiera de los dos prefijos en las fichas.
- `AGENTES.md` escribe las rutas relativas a «la carpeta del pack»; guías y ejemplos usan `uxyngraphar/`.
- Opcional: `uxyngraphar mover-carpeta` (o el panel) mueve `docs/` → `uxyngraphar/` con `git mv`, pone al día solo lo que escribió uxyngraphar (lock, ganchos, reglas para agentes, CODEOWNERS, `.gitignore`, y `CLAUDE.md`/CI si no se cambiaron) y vuelve atrás si algo falla.

### Migración
- `1.1.0-activacion-en-estado`: añade a `ESTADO.md` la línea de activación con las frases del proyecto.

### Correcciones
- Al reescribir un archivo dentro de una actualización se conservan sus permisos (un gancho de git sigue siendo ejecutable).

## [1.0.2] — 2026-10-31

Origen: decisión humana (uxlelmar, 2026-10-31: el repositorio de GitHub pasa a llamarse **uxyngraphar-kit**; y «quiero elegir la carpeta desde la propia interfaz», tras ver que «Examinar…» fallaba en Linux sin selector del sistema; publicar como **v1.0.2**). Aplica a **ambos packs**. Parche: sin cambios de reglas, de estructura del pack ni migraciones.

### Herramienta (`uxyngraphar`)
- **Repositorio renombrado:** las descargas, el instalador de una línea y los enlaces usan `https://github.com/uxlelmar-eaac/uxyngraphar-kit`. GitHub redirige el nombre anterior, así que las instalaciones 1.0.0 y 1.0.1 siguen encontrando las versiones nuevas con `uxyngraphar autoactualizar`.
- **Explorador de carpetas en la página:** todos los botones «Examinar…» (asistente de instalación, panel → «Añadir un proyecto que ya tiene uxyngraphar», asistente de actualización) abren un explorador dentro de la misma página: ruta pulsable, cuadro para escribir la ruta, atajos (carpeta personal, Escritorio, Documentos, proyectos registrados y unidades en Windows), subcarpetas con etiquetas «git» y «uxyngraphar», «Subir», «Mostrar carpetas ocultas», «Cancelar» y «Usar esta carpeta». Ya no depende del selector del sistema ni muestra avisos del navegador. Solo lee nombres de carpetas.

## [1.0.1] — 2026-10-31

Origen: decisión humana (uxlelmar, 2026-10-31: pasar toda la documentación a `español/documentacion/`, mejorar cómo se ve la consola y publicar el resultado como **v1.0.1**). Aplica a **ambos packs**. Parche: sin cambios de reglas, de estructura del pack ni migraciones.

### Herramienta (`uxyngraphar`)
- **Panel:** configuraciones rápidas en la pestaña de plantilla, pestaña de atajos y comandos, textos más claros en respaldos y memoria del sistema, y la versión actual con un botón para actualizar en un clic cuando hay una nueva publicada.
- **Consola más clara y con color:** la ayuda agrupa los comandos (Empezar, Tus proyectos, La herramienta) y se ajusta al ancho de la terminal; `uxyngraphar ayuda <comando>` muestra la sintaxis completa y las opciones. Marcas únicas ✓ ! ✕ (con equivalente ASCII), color solo en terminales y respetando `NO_COLOR`.
- **Corrección:** `uxyngraphar autoactualizar` (y el instalador de una línea) ya no abre el panel cuando la versión ya estaba instalada.

### Documentación
- Toda la documentación del kit vive en `español/documentacion/` (manual para personas y agentes); `español/README.md`, `INDICE.md` y `AGENTES.md` quedan como punteros cortos. Nueva guía `08-referencia/mantener-kit.md` y enlaces rotos corregidos.

## [1.0.0] — 2026-10-30

Origen: decisión humana (uxlelmar, 2026-10-30: publicar el estado actual como **uxyngraphar-v1.0.0**, historial git limpio; y «arregla todo eso y todo lo que te encuentres a tu paso en todo el proyecto uxyngraphar, todo alineado a v1.0.0, incluso las nuevas modificaciones»). Aplica a **ambos packs**. Primera versión publicada: línea base pública, sin versiones anteriores.

### Protocolo y reglas
- Packs backend (servidor / API, fuente de verdad de `15-rutas/`) y frontend (cliente / UI) autosuficientes, con protocolo **R-01–R-25** (`PROTOCOLO.md`, resumen en `REGLAS.md`) y paridad gobernada por `PARIDAD-PACKS.md` (`verificar-paridad.py`).
- Organización por estados y fechas (R-17), alcance de `46-evolucion-documentacion` (R-18), límite de líneas (R-19) y núcleo inviolable (R-20).
- Ampliación del alcance de código con aprobación humana (R-21), idioma del código del producto (R-22) y nombres autoexplicativos (R-23).
- **Memoria del sistema** (R-24): nada se borra; las fichas que cumplieron su ciclo pasan a `95-memoria/`, fuera del alcance del agente (reglas deny, exclusiones, CODEOWNERS) y con integridad comprobada (`memoria.py`).
- **Ajustes locales y envío de sugerencias** (R-25): `97-ajustes-locales/` aplica una EVO aprobada sin editar el núcleo (`ajustes.py`); colaborar enviando fichas EVO es opcional, apagado por defecto y solo lo activa una persona (nunca el agente).
- **Reglas del proyecto** en `96-reglas-proyecto/` (esqueleto vacío; el equipo escribe las suyas con `reglas.py`, excepciones en la instrucción).

### Núcleo y herramientas del pack
- Instalación (`instalar-pack.py`) y actualización garantizada (`actualizar-pack.py`): transacción todo o nada, prueba de humo, registro de migraciones (vacío en esta línea base), contrato de compatibilidad para ganchos y CI, y lock recuperable.
- Control de construcción (`controlar.py`, ganchos de git y workflow de CI), verificación del núcleo y del espejo, `doctor.py`, validador de documentación y escáner de secretos.
- Decisiones en consola (`decisiones.py`: pendientes, aplicar, cerrar, depurar hacia la memoria), contexto y presupuesto para la IA (`contexto.py`, `presupuesto.py`, `costo-tokens.py`), mapa del espejo, flota y exportación de EVO.
- Copias de seguridad con política de conservación y restauración (`respaldos.py`).
- Configuración del proyecto en `docs/uxyngraphar.config.json` con validación.

### Herramienta (`uxyngraphar`)
- Instalador de una línea desde la release de GitHub (huella SHA256 verificada, sin `sudo`), con panel de bienvenida en el navegador o consola (`--consola`, CI o agente).
- **`uxyngraphar panel`**: proyectos registrados (versión, salud, actualizar, instalar), configuración de cada uno con vista previa y copia de seguridad, colaborar Sí/No y plantilla de configuración del equipo (`plantilla-config.json`) para proyectos nuevos.
- `instalar`, `actualizar` (`--todos`), `estado`, `proyectos`, `configuracion`, `autoactualizar`, `usar`, `version` y `desinstalar`; asistentes en el navegador para instalar y actualizar desde un clon.
- Pregunta de colaboración al instalar o actualizar (Sí / No, sin opción marcada; en CI o con un agente queda pendiente para la persona); el receptor oficial es el backend de uxyngraphar y un fallo de red solo avisa, nunca rompe la instalación.

### Documentación
- Guías: instalación, configuración (`configuracion-uxyngraphar.md`), control de construcción, actualizar el núcleo, respaldos, memoria, reglas del proyecto, ajustes locales, envío de sugerencias, costo de tokens y elección de pack.
- Manual público del kit en `documentacion/` (fuera de los packs).
