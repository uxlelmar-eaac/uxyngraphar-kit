# Mapa de capas — espejos entre repos

Cuando backend y frontend viven en repos separados, cada uno tiene su propio espejo bajo `docs/50-sistema-integral/`.

| Capa | Repositorio | Espejo documental | Detalle operativo IA |
|------|-------------|-------------------|----------------------|
| Backend (este) | `<org>/<repo-backend>` | `docs/50-sistema-integral/<rutas-src>/` | `25-areas/`, `15-rutas/` |
| Frontend | `<org>/<repo-frontend>` | `docs/50-sistema-integral/<rutas-app>/` | `25-areas/`, `15-rutas/` BFF |

## Correspondencia por dominio (rellenar al adoptar)

| Dominio / feature | Carpeta espejo backend | Carpeta espejo frontend |
|-------------------|------------------------|-------------------------|
| `<ej. auth>` | `50-sistema-integral/src/modules/auth/` | `50-sistema-integral/src/app/(auth)/` |
| `<ej. users>` | `…` | `…` |

## Regla

Misma feature → mismas filas en esta tabla. Los `.md` de cada espejo describen **su capa**; enlazar al otro repo por ruta de espejo, no duplicar fichas HTTP.
