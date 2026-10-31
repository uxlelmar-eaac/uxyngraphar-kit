# Versión del núcleo

```yaml
version: 1.0.1
fecha: 2026-10-31
```

## Historial

- `1.0.1` — Parche: panel más claro (configuraciones rápidas, pestaña de atajos y comandos, versión actual y actualizar con un clic), toda la documentación del kit reunida en `español/documentacion/` y consola más clara y con color (ayuda por grupos y `uxyngraphar ayuda <comando>`). Sin cambios de reglas ni de estructura del pack. Aplica a ambos packs.
- `1.0.0` — Primera versión publicada de **uxyngraphar**. Packs backend y frontend autosuficientes con protocolo R-01–R-25, instalación y actualización, control de construcción, CI, núcleo inviolable, memoria del sistema, reglas del proyecto, ajustes locales y envío de sugerencias, panel visual (`uxyngraphar panel`) para proyectos, configuración y plantilla del equipo, e instalador interactivo. Aplica a ambos packs.

## Reglas semver

- `MAYOR`: cambio incompatible (renombra secciones, cambia frontmatter
  obligatorio, elimina reglas).
- `MENOR`: sección, especificación o plantilla nueva compatible.
- `PARCHE`: corrección de enlaces, typos, aclaraciones sin cambio de regla.

Cada release actualiza este archivo y la línea **Versión:** de [README.md](README.md) en ambos espejos el mismo día.
