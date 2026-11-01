# Salud del proyecto (doctor)

## En el panel

`uxyngraphar` → **Mis proyectos** → «Abrir» → **Salud**.

- Lista primero lo urgente: errores, avisos e información, cada uno con su arreglo («→»). Lo que está bien queda plegado.
- **«Arreglar»** aplica las correcciones **seguras**: termina o deshace una actualización a medias; repone `.gitignore`/`.gitattributes`, las reglas deny para agentes, el bloque de CODEOWNERS, las frases de activación de `ESTADO.md`, el workflow de CI y el gancho pre-commit. **Nunca** reescribe el núcleo ni tu contenido.
- Antes de tocar nada enseña qué hace y qué archivos puede cambiar, y guarda una copia (se restaura en **Copias de seguridad**). Al terminar dice qué archivos cambiaron de verdad: revísalos y haz commit.

## Qué hacer si marca errores

1. Lee el mensaje: suele traer el remedio (en el panel, el botón que toca).
2. Actualización a medias / diario abierto → «Arreglar», o vuelve a actualizar.
3. Núcleo tocado a mano → restaura la copia en **Copias de seguridad** o vuelve a actualizar; no «apañes» el núcleo.
4. Secretos detectados → sácalos del árbol y rota credenciales.

## Avanzado: desde la terminal

Desde el proyecto (ajusta la ruta si el `uxyngraphar/` no está en la raíz):

```bash
python3 uxyngraphar/scripts/doctor.py
# Windows: py -3 uxyngraphar/scripts/doctor.py
```

| Flag | Efecto |
|------|--------|
| (ninguno) | Solo lee; no modifica |
| `--fix` | Lo mismo que «Arreglar» (sin la copia previa del panel) |
| `--strict` | Los WARN también hacen fallar |
| `--json` | Salida JSON |
| `--pack RUTA` | Contrasta con una fuente de pack |

Códigos de salida: `0` sano (o solo INFO) · `≠0` hay ERROR (o WARN con `--strict`).

Otros chequeos (los usa el CI; el doctor ya los incluye):

```bash
python3 uxyngraphar/scripts/validar-documentacion.py
python3 uxyngraphar/scripts/decisiones/decisiones.py scan
```

**Nota:** la ruta correcta es `uxyngraphar/scripts/decisiones/decisiones.py` (no `uxyngraphar/scripts/decisiones.py`).
