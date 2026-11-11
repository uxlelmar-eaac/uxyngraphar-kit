# Accesos directos al panel de uxyngraphar: menú de aplicaciones/Inicio, escritorio y barra de tareas/dock/favoritos.
# Va dentro del instalador publicado (publicar.py lo une entre arranque_descarga.py y arranque.py) y lo usa el panel.
# Mismas reglas que arranque_descarga.py: solo biblioteca estándar, sintaxis de Python 3.6, nada se ejecuta al importar.
# Lo creado se anota en instalacion.json («accesos») para que «uxyngraphar desinstalar» lo quite.

import ast
import os
import shutil
import subprocess
import sys

# <solo-repositorio>  (publicar.py quita este bloque: en el archivo publicado arranque_descarga ya va delante)
from arranque_descarga import ES_WINDOWS, PASOS, decir  # noqa: F401
# </solo-repositorio>

ACCESO_MARCA = "uxyngraphar-acceso"
ACCESO_DESKTOP = "uxyngraphar.desktop"
ACCESO_TIPOS = ("menu", "escritorio", "barra")
ENTORNOS_SIN_PERSONA = ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL", "CLAUDECODE", "UXYNGRAPHAR_AGENTE")


def _acc_sistema():
    if os.name == "nt":
        return "windows"
    return "mac" if sys.platform == "darwin" else "linux"


def _acc_ejecutar(orden):
    """Ejecuta un programa del sistema; devuelve (código, salida). Sin el programa, (127, "")."""
    try:
        r = subprocess.run(orden, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                           errors="replace", timeout=30)
        return r.returncode, r.stdout
    except (OSError, subprocess.SubprocessError):
        return 127, ""


def _acc_gnome():
    return "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP", "").upper() and bool(shutil.which("gsettings"))


def accesos_disponibles():
    """Qué accesos se pueden crear en este sistema, con su nombre para personas."""
    sistema = _acc_sistema()
    if sistema == "windows":
        return [{"tipo": "menu", "etiqueta": "Menú Inicio", "posible": True, "nota": ""},
                {"tipo": "escritorio", "etiqueta": "Escritorio", "posible": True, "nota": ""},
                {"tipo": "barra", "etiqueta": "Barra de tareas", "posible": False,
                 "nota": "Windows no deja que un programa se ancle solo: abre el menú Inicio, haz clic derecho en "
                         "uxyngraphar y elige «Anclar a la barra de tareas»."}]
    if sistema == "mac":
        return [{"tipo": "menu", "etiqueta": "Aplicaciones (Launchpad)", "posible": True, "nota": ""},
                {"tipo": "escritorio", "etiqueta": "Escritorio", "posible": True, "nota": ""},
                {"tipo": "barra", "etiqueta": "Dock", "posible": True, "nota": "Para quitarlo del Dock, arrástralo fuera."}]
    gnome = _acc_gnome()
    return [{"tipo": "menu", "etiqueta": "Menú de aplicaciones", "posible": True, "nota": ""},
            {"tipo": "escritorio", "etiqueta": "Escritorio", "posible": True, "nota": ""},
            {"tipo": "barra", "etiqueta": "Favoritos del dock (barra de tareas)", "posible": gnome,
             "nota": "" if gnome else "Tu escritorio no permite anclarlo automáticamente: busca uxyngraphar en el menú de "
                                      "aplicaciones y elige «Añadir a favoritos» o «Anclar»."}]


def _acc_python_sin_consola():
    if os.name == "nt":
        pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        if os.path.isfile(pythonw):
            return pythonw
    return sys.executable


def _acc_icono(home):
    """Copia el icono de la versión activa a la carpeta base (las versiones se podan; el icono debe quedarse)."""
    destino = os.path.join(home, "icono.svg")
    try:
        with open(os.path.join(home, "actual"), encoding="utf-8") as f:
            version = f.read().strip()
        origen = os.path.join(home, "versiones", version, "motor", "web", "icono.svg")
        if os.path.isfile(origen):
            shutil.copyfile(origen, destino)
    except OSError:
        pass
    return destino if os.path.isfile(destino) else ""


def _acc_entre_comillas(texto):
    return '"' + texto.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$") + '"'


def _acc_texto_desktop(lanzador, icono):
    lineas = ["[Desktop Entry]", "# " + ACCESO_MARCA, "Type=Application", "Name=uxyngraphar",
              "Comment=Panel de sistemas de gobernanza para tus proyectos",
              "Exec={} {} panel".format(_acc_entre_comillas(sys.executable), _acc_entre_comillas(lanzador)),
              "Terminal=false", "Categories=Development;Utility;", "StartupNotify=true"]
    if icono:
        lineas.append("Icon=" + icono)
    return "\n".join(lineas) + "\n"


def _acc_aplicaciones_linux():
    datos = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(datos, "applications")


def _acc_escritorio():
    propio = os.environ.get("XDG_DESKTOP_DIR")
    if propio:
        return os.path.expanduser(propio)
    if _acc_sistema() == "linux":
        codigo, salida = _acc_ejecutar(["xdg-user-dir", "DESKTOP"])
        if codigo == 0 and salida.strip() and salida.strip() != os.path.expanduser("~"):
            return salida.strip()
    for nombre in ("Desktop", "Escritorio"):
        ruta = os.path.join(os.path.expanduser("~"), nombre)
        if os.path.isdir(ruta):
            return ruta
    return os.path.join(os.path.expanduser("~"), "Desktop")


def _acc_escribir(ruta, texto, ejecutable=False):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    if ejecutable:
        os.chmod(ruta, 0o755)  # noqa: S103 - lanzador y accesos: ejecutables del usuario (0o755)


def _acc_favoritos():
    codigo, salida = _acc_ejecutar(["gsettings", "get", "org.gnome.shell", "favorite-apps"])
    if codigo != 0:
        return None
    texto = salida.strip()
    if texto.startswith("@as"):
        texto = texto[3:].strip()
    try:
        lista = ast.literal_eval(texto)
    except (ValueError, SyntaxError):
        return None
    return [str(x) for x in lista] if isinstance(lista, (list, tuple)) else None


def _acc_poner_favoritos(lista):
    return _acc_ejecutar(["gsettings", "set", "org.gnome.shell", "favorite-apps", str(list(lista))])[0] == 0


def _acc_linux(home, lanzador, tipos, creados, avisos):
    texto = _acc_texto_desktop(lanzador, _acc_icono(home))
    if "menu" in tipos or "barra" in tipos:
        ruta = os.path.join(_acc_aplicaciones_linux(), ACCESO_DESKTOP)
        _acc_escribir(ruta, texto, ejecutable=True)
        creados.append({"tipo": "menu", "ruta": ruta})
        _acc_ejecutar(["update-desktop-database", _acc_aplicaciones_linux()])
    if "escritorio" in tipos:
        ruta = os.path.join(_acc_escritorio(), ACCESO_DESKTOP)
        _acc_escribir(ruta, texto, ejecutable=True)
        _acc_ejecutar(["gio", "set", ruta, "metadata::trusted", "true"])
        creados.append({"tipo": "escritorio", "ruta": ruta})
    if "barra" in tipos:
        favoritos = _acc_favoritos() if _acc_gnome() else None
        if favoritos is None:
            avisos.append("No pude anclarlo al dock: búscalo en el menú de aplicaciones y elige «Añadir a favoritos».")
        elif ACCESO_DESKTOP not in favoritos and not _acc_poner_favoritos(favoritos + [ACCESO_DESKTOP]):
            avisos.append("GNOME no aceptó el cambio de favoritos; añádelo desde el menú de aplicaciones.")
        else:
            creados.append({"tipo": "barra", "favorito": ACCESO_DESKTOP})


def _acc_powershell_lnk(destino_ps, objetivo, argumentos):
    def ps(texto):
        return "'" + texto.replace("'", "''") + "'"
    guion = ("$d = {}; New-Item -ItemType Directory -Force -Path (Split-Path $d) | Out-Null; "
             "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($d); $s.TargetPath = {}; $s.Arguments = {}; "
             "$s.Description = 'Panel de uxyngraphar'; $s.Save(); Write-Output $d").format(destino_ps, ps(objetivo), ps(argumentos))
    return _acc_ejecutar(["powershell", "-NoProfile", "-NonInteractive", "-Command", guion])


def _acc_windows(lanzador, tipos, creados, avisos):
    argumentos = '"{}" panel'.format(lanzador)
    destinos = {"menu": "Join-Path ([Environment]::GetFolderPath('Programs')) 'uxyngraphar.lnk'",
                "escritorio": "Join-Path ([Environment]::GetFolderPath('Desktop')) 'uxyngraphar.lnk'"}
    for tipo in ("menu", "escritorio"):
        if tipo in tipos:
            codigo, salida = _acc_powershell_lnk("(" + destinos[tipo] + ")", _acc_python_sin_consola(), argumentos)
            if codigo == 0 and salida.strip():
                creados.append({"tipo": tipo, "ruta": salida.strip().splitlines()[-1]})
            else:
                avisos.append("No pude crear el acceso directo ({}).".format(tipo))
    if "barra" in tipos:
        avisos.append("Para anclarlo a la barra de tareas: menú Inicio, clic derecho en uxyngraphar, «Anclar a la barra de tareas».")


def _acc_mac(home, lanzador, tipos, creados, avisos):
    app = os.path.join(os.path.expanduser("~"), "Applications", "uxyngraphar.app")
    if tipos:
        _acc_escribir(os.path.join(app, "Contents", "MacOS", "uxyngraphar"),
                      "#!/bin/sh\n# {}\nexec {} {} panel\n".format(ACCESO_MARCA, _acc_entre_comillas(sys.executable),
                                                                   _acc_entre_comillas(lanzador)), ejecutable=True)
        _acc_escribir(os.path.join(app, "Contents", "Info.plist"),
                      '<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0"><dict>'
                      "<key>CFBundleName</key><string>uxyngraphar</string><key>CFBundleExecutable</key><string>uxyngraphar</string>"
                      "<key>CFBundleIdentifier</key><string>dev.uxlelmar.uxyngraphar</string>"
                      "<key>CFBundlePackageType</key><string>APPL</string></dict></plist>\n")
        creados.append({"tipo": "menu", "ruta": app})
    if "escritorio" in tipos:
        enlace = os.path.join(_acc_escritorio(), "uxyngraphar.app")
        os.makedirs(os.path.dirname(enlace), exist_ok=True)
        if not os.path.lexists(enlace):
            os.symlink(app, enlace)
        creados.append({"tipo": "escritorio", "ruta": enlace})
    if "barra" in tipos:
        dato = ("<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>{}</string>"
                "<key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>").format(app)
        if _acc_ejecutar(["defaults", "write", "com.apple.dock", "persistent-apps", "-array-add", dato])[0] == 0:
            _acc_ejecutar(["killall", "Dock"])
            creados.append({"tipo": "barra", "dock": app})
        else:
            avisos.append("No pude añadirlo al Dock: arrástralo desde la carpeta Aplicaciones.")


def crear_accesos(home, lanzador, tipos, registro):
    """Crea los accesos pedidos y los anota en registro["accesos"]. Devuelve avisos para la persona."""
    tipos = [t for t in tipos if t in ACCESO_TIPOS]
    creados, avisos = [], []
    try:
        sistema = _acc_sistema()
        if sistema == "windows":
            _acc_windows(lanzador, tipos, creados, avisos)
        elif sistema == "mac":
            _acc_mac(home, lanzador, tipos, creados, avisos)
        else:
            _acc_linux(home, lanzador, tipos, creados, avisos)
    except OSError as exc:
        avisos.append("No pude crear todos los accesos directos: {}".format(exc))
    registro["accesos"] = registro.get("accesos", []) + creados
    return avisos


def _acc_es_nuestro(ruta):
    if ruta.endswith(".lnk") or os.path.islink(ruta):
        return True
    objetivo = os.path.join(ruta, "Contents", "MacOS", "uxyngraphar") if ruta.endswith(".app") else ruta
    try:
        with open(objetivo, encoding="utf-8", errors="replace") as f:
            return ACCESO_MARCA in f.read(2000)
    except OSError:
        return False


def quitar_accesos(registro):
    """Quita los accesos anotados en registro["accesos"] (solo los que creó uxyngraphar). Devuelve avisos."""
    avisos = []
    for acceso in registro.get("accesos", []):
        ruta = acceso.get("ruta", "")
        if ruta and os.path.lexists(ruta) and _acc_es_nuestro(ruta):
            if os.path.isdir(ruta) and not os.path.islink(ruta):
                shutil.rmtree(ruta, ignore_errors=True)
            else:
                os.remove(ruta)
        if acceso.get("favorito"):
            favoritos = _acc_favoritos()
            if favoritos and acceso["favorito"] in favoritos:
                _acc_poner_favoritos([f for f in favoritos if f != acceso["favorito"]])
        if acceso.get("dock"):
            avisos.append("Si sigue en el Dock, arrástralo fuera para quitarlo.")
    registro["accesos"] = []
    return avisos


# Preguntas del instalador (se hacen en la terminal de la persona, aunque la entrada estándar sea el instalador).

def abrir_terminal():
    """La terminal de la persona para preguntarle algo aunque la entrada estándar sea el propio instalador
    (curl ... | python3 -). None si no hay una persona delante."""
    if any(str(os.environ.get(v, "")).strip().lower() not in ("", "0", "false") for v in ENTORNOS_SIN_PERSONA):
        return None
    try:
        if not sys.stdout.isatty():
            return None
        return open("CONIN$" if ES_WINDOWS else "/dev/tty", "r", encoding="utf-8", errors="replace")
    except (OSError, AttributeError, ValueError):
        return None


def preguntar_si(terminal, pregunta, defecto):
    sys.stdout.write("{} [{}] ".format(pregunta, "S/n" if defecto else "s/N"))
    sys.stdout.flush()
    respuesta = (terminal.readline() or "").strip().lower()
    PASOS.append("{} {}".format(pregunta, respuesta or ("s" if defecto else "n")))
    if not respuesta:
        return defecto
    return respuesta in ("s", "si", "sí", "y", "yes")


DEFECTO_ACCESOS = {"menu": True, "escritorio": False, "barra": False}


def elegir_accesos(pedidos):
    """Accesos que crear: los de --accesos, ninguno con --sin-accesos, o los que la persona elija en la terminal.
    Devuelve None si no hubo a quién preguntar (el panel de bienvenida lo ofrecerá)."""
    if pedidos is not None:
        return pedidos
    terminal = abrir_terminal()
    if terminal is None:
        return None
    elegidos = []
    with terminal:
        decir("\nAccesos directos para abrir el panel sin usar la terminal:", "seccion")
        for d in accesos_disponibles():
            if not d["posible"]:
                decir("  " + d["nota"], "paso")
                continue
            texto = "  ¿Crear acceso directo en {}?".format(d["etiqueta"]) if d["tipo"] != "barra" else "  ¿Anclarlo a {}?".format(d["etiqueta"])
            if preguntar_si(terminal, texto, DEFECTO_ACCESOS[d["tipo"]]):
                elegidos.append(d["tipo"])
    return elegidos


def aplicar_accesos(home, lanzador, tipos, registro):
    if not tipos:
        return
    for aviso in crear_accesos(home, lanzador, tipos, registro):
        decir("  " + aviso, "aviso")
    hechos = sorted({a["tipo"] for a in registro.get("accesos", [])})
    if hechos:
        decir("  Accesos directos creados: {}.".format(", ".join(hechos)), "ok")
