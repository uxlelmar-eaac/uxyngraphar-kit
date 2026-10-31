# Instalar la herramienta `uxyngraphar`

Una vez por equipo/máquina.

## Linux / macOS

```bash
curl -fsSL https://github.com/uxlelmar-eaac/uxyngraphar/releases/latest/download/instalar-uxyngraphar.py | python3 -
```

## Windows (PowerShell)

```powershell
irm https://github.com/uxlelmar-eaac/uxyngraphar/releases/latest/download/instalar-uxyngraphar.py | py -
```

Si no tienes `py`, usa `python`.

## Qué ocurre

1. Descarga por HTTPS y verifica **SHA256**.
2. Instala bajo `~/.uxyngraphar/` (Windows: `%LOCALAPPDATA%\uxyngraphar\`).
3. Expone el comando `uxyngraphar` (suele quedar en `~/.local/bin/` o el `bin` de la herramienta en Windows).
4. Puede abrir el **panel** local (`panel --bienvenida`).

## PATH / «command not found»

1. Cierra y abre la terminal (el instalador puede haber tocado `.bashrc` / `.zshrc` / PATH de usuario).
2. Comprueba: `uxyngraphar version`
3. Si instalaste con `--sin-path`, añade a mano el `bin` de la herramienta al PATH o invoca `python3 ~/.uxyngraphar/…` según la estructura instalada.
4. Variables: `UXYNGRAPHAR_HOME` (cambia la carpeta base; el comando queda en `<carpeta>/bin` y no se toca el PATH), `UXYNGRAPHAR_BIN` (carpeta del comando), `UXYNGRAPHAR_SIN_PATH`.

## Opciones del instalador de una línea

- `--version X.Y.Z` — versión fija (o usa `download/vX.Y.Z` en la URL)
- `--sin-path` — no tocar PATH ni perfiles
- `--consola` — no abrir el panel al terminar
- Revisar antes: descarga el `.py`, léelo, luego ejecútalo

## Desinstalar solo la herramienta

```bash
uxyngraphar desinstalar
```

No borra `docs/` de tus proyectos. Ver [../05-comandos/referencia-cli.md](../05-comandos/referencia-cli.md).
