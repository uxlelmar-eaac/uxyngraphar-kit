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

## Si algo queda a medias

- Revisa `.uxyngraphar-respaldo/` y `uxyngraphar/10-guias/respaldos.md`
- `python3 uxyngraphar/scripts/doctor.py` (y `--fix` si indica correcciones seguras)
