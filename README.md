# uxyngraphar

Catálogo de **paquetes especializados** humano–IA (portátiles e inmutables) y la herramienta que los instala en tus repos. Por ahora solo en español.

Cada paquete es un entorno de trabajo completo para un conjunto acotado de problemas: qué resuelve y qué no, límites, proceso por fases, skills, herramientas, andamiaje y ejemplos, todo en su carpeta. Una base común (`paquetes/!base/`) es el protocolo que rige la estructura de todos sin limitar su contenido.

Todo está en **`español/`**: el catálogo en `paquetes/` (cada paquete independiente) y todo lo demás en [`motor/`](./español/motor/README.md), con el contrato en [`ESPECIFICACION.md`](./español/motor/ESPECIFICACION.md) y el criterio de diseño en [`GUIA-DE-PAQUETES.md`](./español/motor/GUIA-DE-PAQUETES.md).

```bash
# Linux / macOS
curl -fsSL https://github.com/uxlelmar-eaac/uxyngraphar-kit/releases/latest/download/instalar-uxyngraphar.py | python3 -
```

Después, el único comando que necesitas es **`uxyngraphar`**: abre el panel en tu navegador, donde eliges paquetes y los instalas, actualizas o quitas en tus repos. Si tienes una instalación 1.x, `uxyngraphar migrar --repo RUTA` la lleva a 2.0 (primero simula).

## Licencia

Copyright © 2026 uxleleaac / uxlelmar

Este kit se publica bajo **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**.

- Texto legal: [`LICENSE`](./LICENSE)
- Resumen: [`LICENCIA.md`](./LICENCIA.md)
- Detalle: [`LICENSING.md`](./LICENSING.md)
- Seguridad: [`SECURITY.md`](./SECURITY.md)

El **código** de la aplicación (API y UI) está en otros repositorios bajo **GPL-3.0** (con licencia comercial opcional). Ver `LICENSING.md`.
