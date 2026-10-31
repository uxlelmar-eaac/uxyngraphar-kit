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
| Stack backend | `<p. ej. Node, Python, Go, Java — framework opcional>` |
| Stack frontend | `<p. ej. React, Vue, Angular — o N/A si solo API>` |

## Rutas de código

| Concepto | Ruta en este repo |
|----------|-------------------|
| Módulos de negocio | `<p. ej. src/modules/>` |
| Código transversal | `<p. ej. src/common/>` |
| Punto de entrada HTTP | `<p. ej. src/main.ts, app.py>` |
| Especificación OpenAPI | `<p. ej. /api/docs, openapi.yaml>` |

## Espejo integral (`50-sistema-integral/`)

La documentación integral **replica esta estructura** bajo `docs/50-sistema-integral/` (solo `.md`).

| Campo | Valor |
|-------|-------|
| Raíces a reflejar | `<p. ej. src/, prisma/>` |
| Excluir siempre | `node_modules/`, `dist/`, `build/`, `.git/`, `coverage/`, `docs/` |
| Excluir opcional | `<p. ej. test/fixtures/, **/*.spec.ts>` |
| Convención | `README.md` por carpeta; `<nombre-base>.md` paralelo a archivo de código |

Generación: instrucción [`_PLANTILLA-generar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md). Protocolo: [`50-sistema-integral/_PROTOCOLO.md`](../50-sistema-integral/_PROTOCOLO.md).

## Repos relacionados

| Rol | Repositorio | Notas |
|-----|-------------|-------|
| Cliente (UI) | `<org>/<repo-frontend>` | Citas por ID de endpoint |
| Servidor (API) | `<org>/<repo-backend>` | Fuente de verdad de `15-rutas/` |

## Convenciones del equipo

- Rama principal: `<main|master>`
- Prefijo de ramas de feature: `<feature/>`
- ¿Monorepo o multi-repo?: `<respuesta>`
- IDs de endpoints compartidos: [registro-ids-compartidos.md](registro-ids-compartidos.md) + fichas en `15-rutas/`

## Convenciones documentales

- Frontmatter: [convenciones-frontmatter.md](convenciones-frontmatter.md)
- Registro ids compartidos (multi-repo): [registro-ids-compartidos.md](registro-ids-compartidos.md)
- Lo que las herramientas hacen cumplir (controles, idioma, commits, ramas, respaldos) se fija en `docs/uxyngraphar.config.json`: [configuracion-uxyngraphar.md](../10-guias/configuracion-uxyngraphar.md)

## Contacto / ownership

| Área | Responsable |
|------|-------------|
| Documentación | `<equipo o persona>` |
| API | `<equipo o persona>` |
