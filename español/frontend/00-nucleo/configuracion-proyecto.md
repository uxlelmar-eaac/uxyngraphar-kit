# Configuración del proyecto

> **Plantilla.** Rellenar al pegar este pack en un repositorio real. Es la ficha de identidad del proyecto para humanos y agentes.

## Identidad

| Campo | Valor |
|-------|-------|
| Nombre del producto | `<nombre>` |
| Repositorio | `<org>/<repo>` |
| Rol de este pack | `servidor` \| `cliente` \| `monorepo` |
| Versión del pack adoptada | `<versión>` — fuente única: [VERSION.md](../VERSION.md) · historial: [CHANGELOG.md](../CHANGELOG.md) |
| Perfil adoptado | `completo` \| `minimo` — ver [adopcion-pack.md](../10-guias/adopcion-pack.md) |
| Stack frontend | `<p. ej. React, Vue, Angular, Svelte — framework opcional>` |
| Stack backend consumido | `<URL o repo del API>` |

## Rutas de código

| Concepto | Ruta en este repo |
|----------|-------------------|
| Funcionalidades / módulos UI | `<p. ej. src/features/>` |
| Manejadores BFF (si existen) | `<p. ej. app/api/, routes/api/>` |
| Cliente HTTP | `<p. ej. src/lib/api/>` |
| Componentes compartidos | `<p. ej. src/components/shared/>` |

## Espejo integral (`50-sistema-integral/`)

Replica la estructura UI bajo `docs/50-sistema-integral/` (solo `.md`).

| Campo | Valor |
|-------|-------|
| Raíces a reflejar | `<p. ej. src/app/, src/components/, src/lib/>` |
| Excluir siempre | `node_modules/`, `.next/`, `dist/`, `docs/`, `.git/` |
| Convención | `README.md` por carpeta; `<nombre-base>.md` por page/component/handler |

Generación: [`_PLANTILLA-generar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md).

## Repos relacionados

| Rol | Repositorio | Notas |
|-----|-------------|-------|
| Servidor (API) | `<org>/<repo-backend>` | Fichas HTTP en su `docs/15-rutas/` |
| Cliente (este repo) | `<org>/<repo-frontend>` | Solo BFF propios en `15-rutas/` |

## Convenciones del equipo

- Rama principal: `<main|master>`
- Prefijo de ramas de feature: `<feature/>`
- ¿Monorepo o multi-repo?: `<respuesta>`
- IDs del API: [registro-ids-compartidos.md](registro-ids-compartidos.md); fichas HTTP en repo servidor

## Convenciones documentales

- Frontmatter: [convenciones-frontmatter.md](convenciones-frontmatter.md)
- Registro ids compartidos: [registro-ids-compartidos.md](registro-ids-compartidos.md)
- Lo que las herramientas hacen cumplir (controles, idioma, commits, ramas, respaldos) se fija en `docs/uxyngraphar.config.json`: [configuracion-uxyngraphar.md](../10-guias/configuracion-uxyngraphar.md)

## Contacto / ownership

| Área | Responsable |
|------|-------------|
| Documentación | `<equipo o persona>` |
| UI / frontend | `<equipo o persona>` |
