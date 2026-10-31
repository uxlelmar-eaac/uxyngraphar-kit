# Validación documental en CI — servidor

Guía para integrar [`validar-documentacion.py`](../scripts/validar-documentacion.py) en pipeline post-adopción del pack backend.

## Comando recomendado (estricto)

Atajo — activa todos los flags estrictos del pack servidor:

```bash
STRICT_ALL=1 DECISIONES_MAX_DAYS=30 python3 docs/scripts/validar-documentacion.py
```

Equivalente explícito:

```bash
STRICT_DECISIONES=1 \
STRICT_VINCULOS=1 \
STRICT_PRESUPUESTO=1 \
DECISIONES_MAX_DAYS=30 \
python3 docs/scripts/validar-documentacion.py
```

## Qué valida cada flag

| Variable | Default | Efecto |
|----------|---------|--------|
| `STRICT_ALL` | `0` | `1` = activa `STRICT_DECISIONES`, `STRICT_VINCULOS` y `STRICT_PRESUPUESTO` |
| `STRICT_DECISIONES` | `0` | `1` = falla si hay decisiones pendientes antiguas (revisión de pendientes) |
| `STRICT_VINCULOS` | `0` | `1` = **falla** si instrucción `done` sin `acto`, sin `vinculos_salida` o con `vinculos_salida` vacío |
| `STRICT_PRESUPUESTO` | `0` | `1` = falla si `lectura_minima` + `espejo_leer` > `presupuesto_max_docs` |
| `DECISIONES_MAX_DAYS` | `30` | Umbral de antigüedad para decisiones |

Además (siempre WARN): plantillas `_PLANTILLA*.md` en `05-instrucciones/` sin bloque **Contrato IA**.

## Modo permisivo (desarrollo local)

```bash
python3 docs/scripts/validar-documentacion.py
```

Emite WARN sin bloquear — útil durante adopción inicial.

## Cuándo activar estricto

- Tras primera instrucción `done` en producción
- En PR que toque `docs/05-instrucciones/` o colas 45/46
- Trimestralmente en revisión de cobertura ([matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md))

## Validador en Python y deriva del espejo

`validar-documentacion.py` (estructura, enlaces, fichas, vínculos y secretos). Flags `STRICT_*` (`STRICT_ALL=1` los activa todos; `STRICT_ESTADOS`, `STRICT_IDS`, `STRICT_ESPEJO` incluidos). Pruebas del tooling: `python3 -I docs/scripts/ejecutar-pruebas.py`.

Deriva del espejo en PRs (código tocado sin instrucción, anclas o espejo sin actualizar):

```bash
python3 docs/scripts/verificar-espejo.py --base origin/main            # WARN
STRICT_ESPEJO=1 python3 docs/scripts/verificar-espejo.py --base origin/main  # falla en CI
```

En CI necesita historial (`fetch-depth: 0`) para resolver la rama base.

## Integridad del núcleo

```bash
python3 docs/scripts/verificar-nucleo.py          # falla (1) si el núcleo fue editado, borrado o ampliado
python3 docs/scripts/verificar-nucleo.py --warn   # solo informa
python3 docs/scripts/verificar-nucleo.py --contra ../uxyngraphar/español/backend   # contrasta con el pack fuente (no confía en el lock)
python3 docs/scripts/doctor.py --pack RUTA_PACK --strict   # diagnóstico integral del protocolo
```

En CI, haz checkout de uxyngraphar en la etiqueta de la versión adoptada y usa `--contra`: así un lock manipulado no engaña a la verificación.

Márcalo como check requerido junto con el validador. Complementa `CODEOWNERS` y las reglas `deny` generadas por `instalar-pack.py --proteger`.

## Revisión de pendientes asociada

> (En Windows: `py -3` en lugar de `python3`.)

```bash
python3 docs/scripts/decisiones/decisiones.py scan
python3 docs/scripts/decisiones/decisiones.py scan
```

Ver [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md).

## Referencias

- [instalacion-docs.md](instalacion-docs.md)
- [tarjeta-referencia-humana.md](tarjeta-referencia-humana.md)

## CI en GitHub Actions (generado)

`instalar-pack.py --proteger` crea `.github/workflows/uxyngraphar.yml` (en un monorepo, `uxyngraphar-<app>.yml` por pack) con: validación documental, `verificar-nucleo.py`, `escanear-secretos.py` y, en PR, `controlar.py --base origin/<rama base>`. No sobrescribe un workflow existente.

Tres condiciones para que proteja de verdad (el `doctor.py` avisa de las dos primeras):

1. **El archivo debe estar en la raíz del repo.** GitHub solo lee `.github/workflows/` de la raíz; un workflow dentro de `backend/.github/workflows/` o `frontend/.github/workflows/` **no se ejecuta nunca**. En un monorepo muévelo a la raíz y usa `working-directory` en los pasos de la app.
2. **Debe ejecutar uxyngraphar.** Un pipeline de build/deploy no sustituye a este: añade los pasos o usa el generado.
3. **Debe ser obligatorio.** En GitHub: Settings → Branches → regla de protección → «Require status checks to pass» → el job `uxyngraphar`. Sin eso, `git commit --no-verify` y un push directo siguen saltando el protocolo.

Otros CI (GitLab, Azure, Jenkins…): copia los mismos cuatro comandos; el doctor reconoce `verificar-nucleo`/`controlar.py` en `.gitlab-ci.yml`, `azure-pipelines.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml` y `.circleci/config.yml`.
