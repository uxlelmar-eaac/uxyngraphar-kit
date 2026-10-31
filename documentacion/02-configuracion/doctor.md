# Doctor y validación

Desde el proyecto con pack instalado (ajusta la ruta si el `docs/` no está en la raíz):

```bash
python3 docs/scripts/doctor.py
# Windows: py -3 docs/scripts/doctor.py
```

## Flags

| Flag | Efecto |
|------|--------|
| (ninguno) | Solo lee; no modifica |
| `--fix` | Aplica correcciones **seguras** (gitignore, gitattributes, deny, CODEOWNERS, CI, lock, gancho…). **Nunca** reescribe núcleo ni contenido C |
| `--strict` | Los WARN también hacen fallar |
| `--json` | Salida JSON |
| `--pack RUTA` | Contrasta con una fuente de pack |

## Códigos de salida (típico)

- `0` — sano (o solo INFO)
- `≠0` — hay ERROR (o WARN si `--strict`)

## Qué hacer si falla

1. Lee el mensaje: suele indicar el remedio (`doctor.py --fix`, restaurar, etc.).
2. Actualización a medias / diario abierto → a menudo `doctor.py --fix` o reintentar actualización.
3. Núcleo tocado a mano → restaurar vía actualizador / respaldos (`docs/10-guias/respaldos.md`), no “apañar” el núcleo.
4. Secretos detectados → sácalos del árbol y rota credenciales.

## Otros chequeos

```bash
python3 docs/scripts/validar-documentacion.py
python3 docs/scripts/decisiones/decisiones.py scan
```

**Nota:** la ruta correcta es `docs/scripts/decisiones/decisiones.py` (no `docs/scripts/decisiones.py`).
