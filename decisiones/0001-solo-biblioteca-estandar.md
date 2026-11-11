# 0001 · Solo biblioteca estándar de Python

- **Estado:** aceptada
- **Fecha:** 2026-11-10

## Contexto

El kit se instala con una línea en equipos de personas que no son necesariamente desarrolladoras de Python, y los paquetes viajan dentro de proyectos de cualquier lenguaje. Cualquier dependencia externa obliga a un gestor de paquetes, a un entorno virtual y a resolver versiones en cada equipo.

## Decisión

El motor, el instalador y los scripts de los paquetes usan solo la biblioteca estándar de Python 3.10 o superior. El instalador publicado además se puede leer con Python 3.6 para avisar con claridad de que el Python es demasiado viejo. Las herramientas de desarrollo (ruff, mypy, coverage) se usan solo en CI y se configuran en `pyproject.toml`.

## Consecuencias

- Instalar es descargar y verificar un zip; nada más.
- Algunas cosas se escriben a mano (frontmatter YAML plano, servidor HTTP del panel con `http.server`).
- Cualquier propuesta que añada una dependencia en tiempo de ejecución necesita un ADR que reemplace este.
