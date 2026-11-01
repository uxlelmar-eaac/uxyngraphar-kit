# Sembrar el pack en un proyecto

## Desde el panel (recomendado)

Abre el panel con `uxyngraphar` → **Mis proyectos** → «Instalar uxyngraphar en un proyecto nuevo». Es un asistente de 5 pasos que enseña el plan exacto antes de escribir nada y registra el proyecto al terminar. (`uxyngraphar instalar` abre el mismo asistente.) En el paso 1 escribe la ruta o pulsa **Examinar…**: se abre un explorador de carpetas dentro de la misma página (no depende del selector del sistema, así funciona igual en Linux, macOS y Windows). Desde ahí entras en las carpetas con un clic, subes con «↑ Subir» o con la ruta de arriba, saltas con los atajos (carpeta personal, Escritorio, Documentos, tus proyectos registrados y, en Windows, las unidades) y eliges con «Usar esta carpeta». Las etiquetas «git» y «uxyngraphar» marcan las carpetas que ya son repositorio o ya tienen uxyngraphar. Las carpetas ocultas aparecen si marcas «Mostrar carpetas ocultas»; `Esc` cierra sin elegir.

## Avanzado: desde la terminal (scripts, agentes, CI)

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

- Pack → `uxyngraphar/` (o `SUB/uxyngraphar/`)
- `AGENTES.md` junto a ese `uxyngraphar/`
- `uxyngraphar/.uxyngraphar.lock` y `uxyngraphar/uxyngraphar.config.json`
- Opcional: protecciones (`--propietario`, `--estricto`, o `--sin-proteger` para omitirlas)
- **No** borra tu contenido de proyecto (clase C)

## Tras sembrar

1. Commit de `AGENTES.md` + `uxyngraphar/` (sin secretos)
2. Configuración → [../02-configuracion/configuracion-proyecto.md](../02-configuracion/configuracion-proyecto.md)
3. Salud: panel → **Proyecto → Salud** ([../02-configuracion/doctor.md](../02-configuracion/doctor.md))
4. Si no quedó registrado (instalado desde la terminal): panel → **Mis proyectos** → «Añadir»
