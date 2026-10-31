# Sembrar el pack en un proyecto

## Con la herramienta (recomendado)

```bash
uxyngraphar instalar /ruta/al/repo
```

Sin ruta abre el asistente en el navegador.

### Un solo pack (raíz del repo)

```bash
uxyngraphar instalar /ruta/al/repo --pack servidor --si --colaborar no
uxyngraphar instalar /ruta/al/repo --pack cliente --si --colaborar no
```

Equivalente desde clon:

```bash
python3 español/instalar.py --proyecto /ruta/al/repo --pack servidor --si --colaborar no
# Windows: py -3 español/instalar.py …
```

### `--si` y colaboración

Con `--si` **y sin** `--colaborar`, la respuesta a «¿Colaborar…?» cuenta como **No**. Para Sí explícito: `--colaborar si`.

### Monorepo: ambos packs en el mismo repo

**No uses solo `--pack ambos` a ciegas.** Con `--si` y sin más flags, el asistente asume mismo repo y subcarpetas típicas `apps/api` / `apps/web`.

Receta explícita:

```bash
uxyngraphar instalar /ruta/monorepo \
  --pack ambos --mismo-repo \
  --sub-servidor apps/api --sub-cliente apps/web \
  --si --colaborar no
```

Si cada app vive en la **raíz** de su árbol (sin `apps/…`):

```bash
# Ajusta a tu layout; "" = raíz relativa al proyecto indicado
python3 español/instalar.py --proyecto /ruta/monorepo --pack ambos --mismo-repo \
  --sub-servidor "" --sub-cliente "" --si --colaborar no
```

Detalle: [../06-packs/monorepo.md](../06-packs/monorepo.md).

### Dos repos (API + UI)

```bash
python3 español/instalar.py \
  --proyecto /ruta/backend --proyecto2 /ruta/frontend \
  --pack ambos --si --colaborar no
```

(Sin `--mismo-repo`. El cliente va en `--proyecto2`.)

## Qué escribe (resumen)

- Pack → `docs/` (o `SUB/docs/`)
- `AGENTES.md` junto a ese `docs/`
- `docs/.uxyngraphar.lock` y `docs/uxyngraphar.config.json`
- Opcional: protecciones (`--propietario`, `--estricto`, o `--sin-proteger` para omitirlas)
- **No** borra tu contenido de proyecto (clase C)

## Tras sembrar

1. Commit de `AGENTES.md` + `docs/` (sin secretos)
2. Configuración → [../02-configuracion/configuracion-proyecto.md](../02-configuracion/configuracion-proyecto.md)
3. Doctor → [../02-configuracion/doctor.md](../02-configuracion/doctor.md)
4. Si usas la herramienta: `uxyngraphar proyectos --agregar /ruta` si no quedó registrado
