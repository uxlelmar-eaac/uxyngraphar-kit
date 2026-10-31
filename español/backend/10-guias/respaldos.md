# Copias de seguridad (respaldos)

Única guía sobre las copias que hace uxyngraphar: dónde quedan, cuánto se conservan, cómo se restauran y cómo se limpian. Cubre solo lo que el propio sistema reemplaza o borra; el código y la documentación del proyecto los protege git.

## Dónde quedan

| Origen | Cuándo se crea | Carpeta | Rutas de dentro |
|--------|----------------|---------|-----------------|
| `actualizacion` | Al aplicar una actualización del pack (asistente o `actualizar-pack.py --apply`) | `.uxyngraphar-respaldo/<AAAAMMDD-HHMMSS>/` (raíz del repo git, también en monorepos) | relativas a la raíz del repo |
| `depuracion` | Reservado. La depuración no borra ni reemplaza fichas (van a la memoria, [memoria.md](memoria.md)), así que normalmente está vacía; `restaurar` y `limpiar` la tratan igual que la otra | `docs/.depuracion/respaldo/<AAAAMMDD-HHMMSS>/` | relativas a `docs/` |

- Ambas carpetas están en `.gitignore` (las añade el instalador; `doctor.py --fix` las repone): **nunca entran en git ni ensucian el código**.
- Cada copia lleva `_respaldo.json`: origen, fecha, versiones (antes → después) y qué archivos guardó o creó.
- Una actualización guarda también `docs/.uxyngraphar.lock` y `90-archivo/cambios-pack.md` tal como estaban, y anota los archivos que creó (nuevos y `*.uxyngraphar-nuevo`): así se puede **deshacer entera**.
- Agentes: no leen estas carpetas ni restauran o borran copias (R-20); es tarea humana.

## Cuánto se conservan

Política en `docs/uxyngraphar.config.json`:

```json
"respaldos": {"conservar_dias": 30, "conservar_minimo": 3, "limpieza_automatica": true}
```

- Una copia caduca cuando supera `conservar_dias`, **salvo** las `conservar_minimo` más recientes de cada origen, que se guardan siempre.
- Con `limpieza_automatica: true` las caducadas se borran solas al terminar cada actualización o depuración. Con `false` solo se avisa.
- `doctor.py` informa de las copias caducadas en ambas carpetas y de cómo borrarlas.

## Comandos

```bash
python3 docs/scripts/respaldos.py listar                        # todas, con política, antigüedad y versiones
python3 docs/scripts/respaldos.py ver actualizacion/20261026-090000
python3 docs/scripts/respaldos.py restaurar actualizacion/20261026-090000             # simula
python3 docs/scripts/respaldos.py restaurar actualizacion/20261026-090000 --aplicar   # restaura
python3 docs/scripts/respaldos.py restaurar depuracion/20261026-090000 --archivo 45-mejoras-propuestas/06-listas-para-eliminar/2026-02-01/MEJ-x.md --aplicar
python3 docs/scripts/respaldos.py limpiar                       # qué caducó (simula)
python3 docs/scripts/respaldos.py limpiar --aplicar             # borra lo caducado ya
```

En un monorepo añade `--docs apps/api/docs`. `--aplicar` exige una persona en la terminal (o `UXYNGRAPHAR_HUMANO=1`).

## Restaurar

1. `listar` y `ver` para elegir la copia y comprobar qué contiene.
2. `restaurar ID` sin `--aplicar`: muestra qué vuelve y qué se retira.
3. Con `--aplicar`: **antes de tocar nada guarda el estado actual en una copia nueva**, así la restauración también se puede deshacer.
4. Revisa con `git status`, valida (`validar-documentacion.py`, `verificar-nucleo.py`) y haz commit.

- **Deshacer una actualización:** restaura la copia entera. Vuelven los archivos y el lock anteriores y se retiran los que creó la actualización; el núcleo queda íntegro respecto al lock.
- **Parte de una actualización** (`--archivo`): posible, pero el núcleo quedará distinto del lock y `verificar-nucleo` lo marcará. Úsalo solo para recuperar un archivo tuyo (plantilla o índice).
- **Ficha guardada en la memoria:** no es un respaldo; se recupera con `memoria.py recuperar ID` ([memoria.md](memoria.md)).

Relacionado: [actualizar-nucleo.md](actualizar-nucleo.md) · depuración en la herramienta [decisiones-pendientes](../35-herramientas/autorizadas/decisiones-pendientes.md).
