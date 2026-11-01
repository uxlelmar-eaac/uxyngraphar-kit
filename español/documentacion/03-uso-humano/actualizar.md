# Actualizar el núcleo

```bash
uxyngraphar actualizar /ruta
uxyngraphar actualizar --todos
```

Desde clon:

```bash
python3 español/actualizar.py /ruta
python3 español/actualizar.py /ruta --consola --si --colaborar no
```

## Qué hace

1. Simula el cambio
2. Respalda en `.uxyngraphar-respaldo/`
3. Actualiza **solo el núcleo**
4. Conflictos → `*.uxyngraphar-nuevo` para que decidas
5. Puede añadir protecciones nuevas

## Qué no hace

- No borra tu contenido C
- **Salto de versión MAYOR** (p. ej. 2.x → 3.0): `uxyngraphar actualizar` / `actualizar.py` lo **rechazan**. Hace falta el flujo del pack:

```bash
python3 uxyngraphar/scripts/actualizar-pack.py RUTA_AL_PACK --apply --migracion-aprobada <id-instruccion>
```

La instrucción debe estar aprobada. Guía: `uxyngraphar/10-guias/actualizar-nucleo.md`.

## Proyectos con el pack en `docs/` (instalados antes de la 1.1.0)

Actualizar **no** cambia la carpeta: el pack sigue en `docs/` y todo funciona igual. Si prefieres que se llame `uxyngraphar/` (no choca con tu propia documentación y deja claro qué es), muévela **cuando tú decidas**, después de actualizar a la 1.1.0:

```bash
uxyngraphar mover-carpeta /ruta          # muestra qué cambiaría y qué enlaces tuyos revisar; pregunta antes de mover
uxyngraphar mover-carpeta /ruta --si     # mueve sin preguntar
uxyngraphar mover-carpeta /ruta --a docs # volver a docs/
```

O en el panel: **Configuración del proyecto → Carpeta del sistema → Ver qué cambia → Mover**.

- Exige que `docs/` no tenga cambios sin commit, y que no exista ya `uxyngraphar/`.
- Usa `git mv` (git lo ve como un renombrado) y guarda copia de los archivos de la raíz que toca en `.uxyngraphar-respaldo/`. Si algo falla, o el proceso se corta, todo vuelve a como estaba.
- Pone al día solo lo que escribió uxyngraphar: el lock, los ganchos de git, las reglas para agentes de `.claude/settings.json`, el bloque de `.cursorignore`/`.geminiignore`/`.aiexclude` y de `.github/CODEOWNERS`, y sus líneas de `.gitignore`/`.gitattributes`. `CLAUDE.md` y el workflow de CI, solo si siguen como los dejó uxyngraphar; si los cambiaste, te dice qué línea cambiar.
- Te lista los sitios de tu proyecto que mencionan `docs/` (README, enlaces, scripts propios) para que decidas si apuntan al pack.
- Después: `git status`, revisa y haz commit.

## Si algo queda a medias

- Revisa `.uxyngraphar-respaldo/` y `uxyngraphar/10-guias/respaldos.md`
- `python3 uxyngraphar/scripts/doctor.py` (y `--fix` si indica correcciones seguras)
