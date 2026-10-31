# Arquitectura del cliente

Simetría conceptual con el servidor. Detalle de capas: [plantilla-modulo.md](plantilla-modulo.md). Adapta carpetas y rutas al stack del proyecto.

## Capas (orientativo)

| Carpeta | Rol |
|---------|-----|
| `api/` | Transporte HTTP (petición saliente / JSON crudo) |
| `reception/` | Adapta JSON del servidor → forma de vista (sin JSX) |
| `hooks/` | Estado remoto; orquesta `api` + `reception` |
| `components/` | UI; sin lógica de red |
| `model/` | Utilidades puras (claves de consulta, formatos) |
| `types/` | DTOs y view models |
| `integrations/` | Llamadas al `api/` de otro dominio |
| `styles/` | Estilos acotados a la funcionalidad |

## Reglas

- No importar hooks/components de otro dominio salvo props, layouts compartidos o `common/`.
- Estado remoto según la librería acordada en el proyecto.
- Rutas y grupos de layout según la convención del framework (documentar en este archivo al adaptar).
- Contratos: regenerar tipos cuando cambie el API del servidor.

## Relación con el servidor

La superficie HTTP canónica vive en **`docs/15-rutas/` del repositorio servidor**. Aquí solo se documentan manejadores propios del cliente (si existen) y se citan ids/rutas del API desde `25-areas/*/CONTEXTO.md`.
