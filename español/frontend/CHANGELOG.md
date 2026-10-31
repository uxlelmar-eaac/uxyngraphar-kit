# CHANGELOG — uxyngraphar (pack documental)

Evolución versionada del pack. Este archivo **viaja dentro de cada pack**: el repo que lo adopta registra la versión copiada en `00-nucleo/configuracion-proyecto.md` y se actualiza comparando contra el CHANGELOG de la plantilla más reciente.

Formato: una entrada por lote de cambios; origen (plan/EVO/decisión humana) siempre citado.

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
