# Versión del núcleo

```yaml
version: 1.3.0
fecha: 2026-11-02
```

## Historial

- `1.3.0` — Menor: fase de preguntas antes de la instrucción (`03-preguntas/`, config `preguntas` activo por defecto con rondas `[10, 5, 3]`; Q&A en la plantilla de instrucción). EVO-20261102-fase-preguntas. Sin migraciones de formato. Aplica a ambos packs.
- `1.2.2` — Parche: el panel deja las copias de `.uxyngraphar-respaldo/` escribibles tras respaldar archivos congelados (R-20; Windows no podía podar `settings.json`) y las pruebas del instalador descongelan antes de simular alteraciones. Sin migraciones. Aplica a ambos packs.
- `1.2.1` — Parche: núcleo inviolable fail-closed en proyectos (hooks Cursor con `failClosed`, manifiesto, regla `.cursor/rules`, archivos N y carpetas del núcleo en solo lectura; doctor ERROR si falta protección; `niveles.nucleo` obligado a bloqueante; restaurar/deshacer/lock respetan el congelado). Sin migraciones. Aplica a ambos packs.
- `1.2.0` — Menor: el único comando que necesita una persona es `uxyngraphar`, que abre el panel; desde él se hace todo (salud y arreglos, aprobar pendientes, copias de seguridad, memoria, protecciones, versiones, PATH, desinstalar) y se reabre solo tras actualizar. Los comandos siguen para CI, agentes y scripts. Los agentes cierran las instancias que levantan. Sin cambios en el texto de las reglas ni migraciones. Aplica a ambos packs.
- `1.1.0` — Menor: la carpeta del pack pasa a llamarse `uxyngraphar/` en las instalaciones nuevas (las anteriores siguen en `docs/`; moverlas es opcional con `uxyngraphar mover-carpeta`) y las frases que activan el protocolo («sigue el protocolo uxyngraphar | uxyn | uxynar») se configuran en `protocolo.alias`. Sin cambios en el texto de las reglas. Una migración automática (línea de activación en `ESTADO.md`). Aplica a ambos packs.
- `1.0.2` — Parche: el repositorio pasa a llamarse `uxlelmar-eaac/uxyngraphar-kit` (enlaces y descargas apuntan ahí; el nombre anterior sigue redirigiendo) y «Examinar…» abre un explorador de carpetas dentro de la página en lugar del selector del sistema. Sin cambios de reglas ni de estructura del pack. Aplica a ambos packs.
- `1.0.1` — Parche: panel más claro (configuraciones rápidas, pestaña de atajos y comandos, versión actual y actualizar con un clic), toda la documentación del kit reunida en `español/documentacion/` y consola más clara y con color (ayuda por grupos y `uxyngraphar ayuda <comando>`). Sin cambios de reglas ni de estructura del pack. Aplica a ambos packs.
- `1.0.0` — Primera versión publicada de **uxyngraphar**. Packs backend y frontend autosuficientes con protocolo R-01–R-25, instalación y actualización, control de construcción, CI, núcleo inviolable, memoria del sistema, reglas del proyecto, ajustes locales y envío de sugerencias, panel visual (`uxyngraphar panel`) para proyectos, configuración y plantilla del equipo, e instalador interactivo. Aplica a ambos packs.

## Reglas semver

- `MAYOR`: cambio incompatible (renombra secciones, cambia frontmatter
  obligatorio, elimina reglas).
- `MENOR`: sección, especificación o plantilla nueva compatible.
- `PARCHE`: corrección de enlaces, typos, aclaraciones sin cambio de regla.

Cada release actualiza este archivo y la línea **Versión:** de [README.md](README.md) en ambos espejos el mismo día.
