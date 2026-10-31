# Instalación del pack documental (servidor)

Guía **única vez** al incorporar este scaffolding en un repositorio backend/API.

## Resultado esperado en el repo

```
<repo-backend>/
├── AGENTES.md              ← copiar desde la raíz de este pack (y AGENTS.md, alias)
└── docs/
    ├── INDICE.md           ← este pack completo
    ├── PROTOCOLO.md
    ├── 00-nucleo/
    ├── 05-instrucciones/01-pendientes/…
    ├── … (resto de taxonomía)
```

## Instalación automatizada (recomendada)

Desde un clon de uxyngraphar (el pack del rol que corresponda: `español/backend` o `español/frontend`):

```bash
python3 RUTA/AL/PACK/scripts/instalar-pack.py RUTA/AL/PACK --repo . --proteger --propietario @tu-usuario
```

(En Windows: `py -3` en lugar de `python3`.)

Copia solo el **núcleo** (N), las plantillas (P) y los índices (M); nunca el contenido de otros proyectos. Escribe `docs/.uxyngraphar.lock` (línea base para actualizar), añade `.decisiones/` y `.uxyngraphar-respaldo/` al `.gitignore`, copia `AGENTES.md` a la raíz y valida. Opciones: `--perfil minimo`, `--dry-run`, `--docs <carpeta>`, `--claude-md` (crea `CLAUDE.md` que apunta a `AGENTES.md`) y `--analizar` (informe de dónde encajaría la documentación que el proyecto ya tiene; no escribe nada). El primer argumento puede ser también un `.zip` generado con `scripts/empaquetar-pack.py` (lleva manifiesto con hashes y se verifica antes de instalar). Si el proyecto **ya tiene** `docs/`: `--adoptar` (no pisa nada; lo distinto queda como `<archivo>.uxyngraphar-nuevo`).

Los pasos manuales siguientes siguen valiendo como referencia de lo que hace el instalador.

## Pasos

1. Copiar el contenido de este pack a `docs/` del repo (no subcarpetas sueltas). `PARIDAD-PACKS.md` no hace falta: solo sirve en el repo fuente.
2. Copiar `AGENTES.md` a la **raíz** del repo (junto a `package.json`, `pyproject.toml`, etc.).
3. Rellenar [`00-nucleo/configuracion-proyecto.md`](../00-nucleo/configuracion-proyecto.md): nombre, stack, rutas de código, repo cliente si aplica.
4. Adaptar [`00-nucleo/arquitectura.md`](../00-nucleo/arquitectura.md) y [`restricciones.md`](../00-nucleo/restricciones.md) al stack real.
5. Verificar carpetas operativas listas:
   - Estados de auditorías: `40-auditorias/01-pendientes/` … `40-auditorias/06-listas-para-eliminar/` (con `YYYY-MM-DD/`)
   - `05-instrucciones/`, `20-decisiones/`, `15-rutas/`, `25-areas/`, **`35-herramientas/propuestas/`**, **`45-mejoras-propuestas/`**, **`46-evolucion-documentacion/`**, **`50-sistema-integral/`** (estados e índices vacíos OK)
6. Crear **primera área** de negocio: copiar [`25-areas/_PLANTILLA.md`](../25-areas/_PLANTILLA.md) → `25-areas/<id>/CONTEXTO.md` + fila en INDICE.
7. Por cada endpoint HTTP existente: ficha en `15-rutas/<módulo>/` + filas en índices.
8. (Opcional) Enlazar en el README del repo: “Documentación en `docs/`; agentes IA → `AGENTES.md`”.

## Primera tarea con IA

No implementar sin instrucción. Crear desde [`05-instrucciones/_PLANTILLA.md`](../05-instrucciones/_PLANTILLA.md) con `lectura_minima` y pedir aprobación. Ver [eficiencia-ia.md](../00-nucleo/eficiencia-ia.md).

## Monorepo (backend + frontend en un repo)

Ver [monorepo-docs-fusionados.md](monorepo-docs-fusionados.md).

## No duplicar

- Este pack **es** el scaffolding; no crear otra carpeta `docs-scaffold/` ni `documentacion-plantilla/` en el repo.
- Mantener taxonomía `00`–`90`; no renombrar carpetas numeradas.

## Smoke post-instalación

Verificar antes de dar por cerrada la instalación:

- [ ] `AGENTES.md` (y alias `AGENTS.md`) existe en **raíz** del repo y enlaza a `docs/`
- [ ] `docs/INDICE.md` y `docs/PROTOCOLO.md` presentes
- [ ] Carpetas de estado OK: `05-instrucciones/01-pendientes/`, `20-decisiones/01-pendientes/`, `40-auditorias/02-en-progreso/`, `45-mejoras-propuestas/01-pendientes/`, `46-evolucion-documentacion/01-pendientes/`, `35-herramientas/propuestas/01-pendientes/` (cada una con `YYYY-MM-DD/`)
- [ ] `00-nucleo/configuracion-proyecto.md` sin placeholders críticos (`<nombre>`, `<org/repo>`)
- [ ] Colas `35-herramientas/propuestas/`, `45-mejoras-propuestas/` y `46-evolucion-documentacion/` vacías (solo README de estados, plantillas e índices)
- [ ] El pack ya viene **sin** fichas de ejemplo ni capacitación
- [ ] (Opcional) `python3 docs/scripts/validar-documentacion.py` sin errores
- [ ] (Opcional) `python3 docs/scripts/decisiones/decisiones.py scan` — revisión de pendientes OK
- [ ] Verificar `.gitignore` del repo incluye `.decisiones/` (sesión e historial de decisiones)
- [ ] Registrar **versión del pack adoptada** en [configuracion-proyecto.md](../00-nucleo/configuracion-proyecto.md) (ver [CHANGELOG.md](../CHANGELOG.md) en la raíz de este pack)
- [ ] (Opcional CI estricto) ver [ci-validacion-documentacion.md](ci-validacion-documentacion.md)
- [ ] Primera instrucción o [_PLANTILLA-adopcion-inicial-pack.md](../05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md) lista para aprobar
