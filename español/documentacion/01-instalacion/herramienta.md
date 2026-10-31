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
4. Al terminar abre el **panel** en tu navegador (solo en tu equipo) con todo lo que pasó en la terminal y lo que queda por decidir: añadir el comando al PATH, tu plantilla de configuración e instalar en tu primer proyecto. Sin escritorio, en CI o con `--consola`, todo sigue en la terminal.

Cada proyecto lleva su copia del pack en `docs/` (va en git) y su versión en `docs/.uxyngraphar.lock`, así que pueden convivir proyectos en versiones distintas y quien clona el proyecto no necesita la herramienta.

## Dónde queda

- Herramienta: `~/.uxyngraphar/` (Windows: `%LOCALAPPDATA%\uxyngraphar\`; cambia con `UXYNGRAPHAR_HOME`).
- Comando: `~/.local/bin/uxyngraphar` (Windows: `%LOCALAPPDATA%\uxyngraphar\bin\uxyngraphar.cmd`, generado al instalar). Si hace falta, el instalador añade esa carpeta al PATH (bloque marcado en tu `.bashrc`/`.zshrc`, o PATH de usuario en Windows). Nunca pide `sudo`.

## Seguridad

Descarga por HTTPS, comprueba la huella SHA256 de la versión antes de escribir nada, rechaza rutas peligrosas del zip y, si la descarga se corta, el instalador no ejecuta nada. Volver a ejecutarlo es seguro.

## PATH / «command not found»

1. Cierra y abre la terminal (el instalador puede haber tocado `.bashrc` / `.zshrc` / PATH de usuario).
2. Comprueba: `uxyngraphar version`
3. Si instalaste con `--sin-path`, añade a mano el `bin` de la herramienta al PATH o invoca `python3 ~/.uxyngraphar/…` según la estructura instalada.
4. Variables: `UXYNGRAPHAR_HOME` (cambia la carpeta base; el comando queda en `<carpeta>/bin` y no se toca el PATH), `UXYNGRAPHAR_BIN` (carpeta del comando), `UXYNGRAPHAR_SIN_PATH`.

## Opciones del instalador de una línea

- `--version X.Y.Z` — versión fija (o cambia `latest/download` por `download/v1.0.1` en la URL)
- `--sin-path` — no tocar PATH ni perfiles
- `--consola` — no abrir el panel al terminar
- Revisar antes: `curl -fsSL <url> -o instalar-uxyngraphar.py`, léelo y luego `python3 instalar-uxyngraphar.py`

## Desinstalar solo la herramienta

```bash
uxyngraphar desinstalar
```

No borra `docs/` de tus proyectos. Ver [../05-comandos/referencia-cli.md](../05-comandos/referencia-cli.md).
