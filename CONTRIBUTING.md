# Contribuir al kit uxyngraphar

Gracias por querer mejorar el kit. Todo el código y la documentación están en español; los mensajes de commit también.

## Preparar el entorno

No hay dependencias que instalar: el kit usa solo la biblioteca estándar de Python (3.10 o superior). Desde `español/`:

```bash
python3 motor/uxyngraphar.py sincronizar-comun
python3 motor/uxyngraphar.py validar
python3 -W error::ResourceWarning -m unittest discover -s motor/pruebas -t motor/pruebas
```

`sincronizar-comun` crea en cada sistema la copia local de `scripts/comun/` (git no la versiona: la fuente única es `sistemas-de-gobernanza/_base/scripts/comun/`). Las pruebas usan una carpeta de uxyngraphar temporal: no tocan tu instalación.

Opcional, como en CI (`.github/workflows/pruebas.yml`): `ruff check español/motor español/sistemas-de-gobernanza/_base`, `mypy` sobre los módulos de la lista de CI (configuración en `pyproject.toml`) y la cobertura con su suelo (`motor/pruebas/cobertura.py`).

## Estilo

- Solo biblioteca estándar en tiempo de ejecución. Las herramientas de desarrollo (ruff, mypy, coverage) se usan solo en CI.
- Nombres en español según [`NOMENCLATURA.md`](español/motor/NOMENCLATURA.md); la estructura de los sistemas según [`ESPECIFICACION.md`](español/motor/ESPECIFICACION.md).
- Cada corrección lleva una prueba que reproduce el fallo; cada función pública, un docstring que diga qué hace.
- Las excepciones al linter van con `noqa` y un motivo.
- Un sistema se crea con el generador (`crear` o `generar desde`), nunca copiando otro a mano. Ver [`GUIA-PARA-AGENTES.md`](español/motor/GUIA-PARA-AGENTES.md).

## Versiones

- La **herramienta** sigue semver en `español/motor/VERSION`: PARCHE para correcciones, MENOR si añade comandos, rutas de API o campos opcionales, MAYOR si rompe algo publicado. Cada versión tiene su entrada en `español/motor/CHANGELOG.md` (una prueba comprueba que coinciden).
- Cada **sistema** tiene su versión en `sistema.json` (`uxyngraphar version <id> parche|menor|mayor`) y su `CHANGELOG.md`. Un cambio que deba llegar a los proyectos instalados exige subir la versión del sistema: `actualizar` solo reconstruye si la versión sube. Eso incluye los cambios de `sistemas-de-gobernanza/_base/scripts/comun/`.
- El **protocolo de sistemas** va por su versión 1: solo cambia si un sistema válido deja de serlo.

## Publicar

1. Con `main` en verde, sube `VERSION`, escribe la entrada del CHANGELOG y haz commit.
2. Crea y sube la etiqueta `vX.Y.Z` (la misma que `VERSION`). El workflow `publicar.yml` ejecuta la matriz de pruebas, genera el zip reproducible, el instalador y `SHA256SUMS`, firma su procedencia (atestaciones de GitHub) y publica la release; después la instala desde la URL pública y, si no arranca, la devuelve a borrador.

Publicar avisa a todas las instalaciones existentes: hazlo solo cuando quieras que se actualicen.

## Decisiones

Las decisiones de diseño del kit están en [`decisiones/`](decisiones/README.md). Si un cambio contradice una, propón antes un ADR nuevo que la reemplace.
