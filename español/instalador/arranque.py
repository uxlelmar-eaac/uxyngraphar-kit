# Segunda parte del instalador de una línea: lanzador «uxyngraphar», PATH, registro y main.
# Ver la cabecera de arranque_descarga.py (va delante en el archivo publicado y fija sus reglas).

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

# <solo-repositorio>  (publicar.py quita este bloque: en el archivo publicado arranque_descarga ya va delante)
from arranque_descarga import *  # noqa: F401,F403
# </solo-repositorio>

LANZADOR = '''#!__PYTHON__
# __MARCA__: lo creó el instalador de uxyngraphar. Se quita con «uxyngraphar desinstalar».
import os
import runpy
import sys

HOME = __HOME__


def main():
    try:
        with open(os.path.join(HOME, "actual"), encoding="utf-8") as f:
            version = f.read().strip()
    except OSError:
        version = ""
    cli = os.path.join(HOME, "versiones", version, "uxyngraphar.py")
    if not version or not os.path.isfile(cli):
        sys.stderr.write("uxyngraphar no está bien instalado en " + HOME + ". Vuelve a ejecutar el comando de instalación de una línea.\\n")
        return 1
    os.environ["UXYNGRAPHAR_HOME"] = HOME
    sys.argv[0] = cli
    runpy.run_path(cli, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _texto_lanzador(home):
    python = sys.executable if " " not in sys.executable else "/usr/bin/env python3"
    return LANZADOR.replace("__PYTHON__", python).replace("__MARCA__", MARCA).replace("__HOME__", repr(home))


def es_nuestro(ruta):
    try:
        with open(ruta, encoding="utf-8", errors="replace") as f:
            return MARCA in f.read(2000)
    except OSError:
        return False


def crear_lanzadores(home):
    """Escribe el comando «uxyngraphar». Devuelve (archivo .py del lanzador, lista de archivos creados)."""
    bin_dir = carpeta_bin(home)
    os.makedirs(bin_dir, exist_ok=True)
    if ES_WINDOWS:
        lanzador = os.path.join(bin_dir, "uxyngraphar-lanzador.py")
        escribir_atomico(lanzador, _texto_lanzador(home))
        cmd = os.path.join(bin_dir, "uxyngraphar.cmd")   # Windows solo reconoce como comando .exe/.cmd/.bat
        # Dos líneas: %ERRORLEVEL% se expande después de ejecutar Python, así el .cmd devuelve su código de salida.
        escribir_atomico(cmd, "@rem {} (generado; no se guarda en el repositorio)\r\n@\"{}\" \"{}\" %*\r\n@exit /b %ERRORLEVEL%\r\n".format(MARCA, sys.executable, lanzador))
        return lanzador, [lanzador, cmd]
    lanzador = os.path.join(bin_dir, "uxyngraphar")
    if os.path.exists(lanzador) and not es_nuestro(lanzador):
        lanzador = os.path.join(home, "bin", "uxyngraphar")
        decir("  Aviso: ya existe otro programa llamado uxyngraphar en {}; no lo toco. El comando queda en {}.".format(bin_dir, lanzador))
        os.makedirs(os.path.dirname(lanzador), exist_ok=True)
    escribir_atomico(lanzador, _texto_lanzador(home))
    os.chmod(lanzador, 0o755)
    return lanzador, [lanzador]


def en_path(carpeta):
    objetivo = os.path.normcase(os.path.realpath(carpeta))
    return any(os.path.normcase(os.path.realpath(p)) == objetivo for p in os.environ.get("PATH", "").split(os.pathsep) if p)


def archivo_perfil(bin_dir):
    casa = os.path.expanduser("~")
    shell = os.path.basename(os.environ.get("SHELL", ""))
    ruta = "$HOME/.local/bin" if bin_dir == os.path.join(casa, ".local", "bin") else bin_dir
    linea = 'export PATH="{}:$PATH"'.format(ruta)
    if shell == "zsh":
        return os.path.join(os.environ.get("ZDOTDIR") or casa, ".zshrc"), linea
    if shell == "bash":
        return os.path.join(casa, ".bash_profile" if sys.platform == "darwin" else ".bashrc"), linea
    if shell == "fish":
        return os.path.join(casa, ".config", "fish", "config.fish"), "set -gx PATH \"{}\" $PATH".format(ruta)
    return os.path.join(casa, ".profile"), linea


def agregar_a_perfil(bin_dir):
    perfil, linea = archivo_perfil(bin_dir)
    actual = ""
    if os.path.isfile(perfil):
        with open(perfil, encoding="utf-8", errors="replace") as f:
            actual = f.read()
    if BLOQUE_INI not in actual:
        os.makedirs(os.path.dirname(perfil), exist_ok=True)
        with open(perfil, "a", encoding="utf-8") as f:
            f.write(("" if not actual or actual.endswith("\n") else "\n") + "\n{}\n{}\n{}\n".format(BLOQUE_INI, linea, BLOQUE_FIN))
    return perfil


def quitar_de_perfil(perfil):
    if not perfil or not os.path.isfile(perfil):
        return False
    with open(perfil, encoding="utf-8", errors="replace") as f:
        lineas = f.read().split("\n")
    fuera, dentro = [], False
    for linea in lineas:
        if linea.strip() == BLOQUE_INI:
            dentro = True
        elif linea.strip() == BLOQUE_FIN and dentro:
            dentro = False
        elif not dentro:
            fuera.append(linea)
    if len(fuera) == len(lineas):
        return False
    escribir_atomico(perfil, "\n".join(fuera).rstrip("\n") + "\n")
    return True


def _path_windows(carpeta, agregar):
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE) as clave:
        try:
            valor, tipo = winreg.QueryValueEx(clave, "Path")
        except FileNotFoundError:
            valor, tipo = "", winreg.REG_EXPAND_SZ
        partes = [p for p in str(valor).split(";") if p]
        igual = [p for p in partes if os.path.normcase(os.path.expandvars(p)).rstrip("\\") == os.path.normcase(carpeta).rstrip("\\")]
        if bool(igual) == agregar:
            return False
        nuevas = partes + [carpeta] if agregar else [p for p in partes if p not in igual]
        tipo = tipo if tipo in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) else winreg.REG_EXPAND_SZ
        winreg.SetValueEx(clave, "Path", 0, tipo, ";".join(nuevas))
    try:   # avisa a Windows para que las terminales nuevas vean el PATH actualizado
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x1A, 0, "Environment", 0x2, 5000, ctypes.byref(ctypes.c_ulong()))
    except Exception:  # noqa: BLE001 - el aviso es cortesía; el PATH ya quedó guardado
        pass
    return True


def asegurar_path(home, registro):
    bin_dir = carpeta_bin(home)
    if home_propio() and not en_path(bin_dir):
        # Carpeta base propia: no toco el PATH ni los perfiles de la persona; solo digo dónde quedó.
        return "El comando quedó en {} (UXYNGRAPHAR_HOME propio): no toqué tu PATH. Añádelo tú si lo quieres en el PATH.".format(bin_dir)
    if ES_WINDOWS:
        if _path_windows(bin_dir, True):
            registro["path_windows"] = bin_dir
            return "Añadí {} a tu PATH de usuario. Abre una terminal NUEVA para usar el comando uxyngraphar.".format(bin_dir)
        return ""
    if en_path(bin_dir):
        return ""
    perfil = agregar_a_perfil(bin_dir)
    registro["perfil"] = perfil
    return "Añadí {} al PATH en {}. Abre una terminal nueva (o ejecuta: export PATH=\"{}:$PATH\").".format(bin_dir, perfil, bin_dir)


def leer_registro(home):
    try:
        with open(os.path.join(home, "instalacion.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


class Candado(object):
    """Evita dos instalaciones a la vez en la misma carpeta (un candado de más de 15 minutos se considera abandonado)."""

    def __init__(self, home):
        self.ruta = os.path.join(home, ".instalando")

    def __enter__(self):
        for _ in range(2):
            try:
                os.close(os.open(self.ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                return self
            except FileExistsError:
                if time.time() - os.path.getmtime(self.ruta) < 900:
                    raise ErrorInstalacion("Hay otra instalación de uxyngraphar en curso. Espera a que termine (o borra {} si no es así).".format(self.ruta))
                os.remove(self.ruta)
        raise ErrorInstalacion("No pude crear {}.".format(self.ruta))

    def __exit__(self, *_):
        try:
            os.remove(self.ruta)
        except OSError:
            pass


ENTORNOS_SIN_PERSONA = ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL", "CLAUDECODE", "UXYNGRAPHAR_AGENTE")


def puede_abrir_panel():
    """Hay una persona delante de una terminal con escritorio: el instalador sigue en el navegador."""
    if any(str(os.environ.get(v, "")).strip().lower() not in ("", "0", "false") for v in ENTORNOS_SIN_PERSONA):
        return False
    try:
        if not sys.stdout.isatty():
            return False
    except (AttributeError, ValueError):
        return False
    return ES_WINDOWS or sys.platform == "darwin" or bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def guardar_bienvenida(home, datos):
    """Lo que pasó en esta instalación (para la pantalla de bienvenida del panel)."""
    datos = dict(datos, pasos=list(PASOS))
    escribir_atomico(os.path.join(home, "ultima-instalacion.json"), json.dumps(datos, indent=2, ensure_ascii=True) + "\n")


def abrir_panel(home):
    """Abre el panel en modo bienvenida con la versión recién activada. Si no puede, deja las instrucciones de la consola."""
    try:
        with open(os.path.join(home, "ultima-instalacion.json"), encoding="utf-8") as f:
            lanzador = json.load(f).get("lanzador", "")
    except (OSError, ValueError):
        lanzador = ""
    if not lanzador or not os.path.isfile(lanzador):
        return 0
    decir("\nAbriendo el panel de uxyngraphar en tu navegador para terminar la configuración...")
    try:
        return subprocess.call([sys.executable, lanzador, "panel", "--bienvenida"])
    except KeyboardInterrupt:
        return 0


def instalar(version, sin_path=False, con_panel=False):
    home = carpeta_home()
    decir("uxyngraphar {} -> {}".format(version, home))
    if not shutil.which("git"):
        decir("  Aviso: no encuentro git. La herramienta se instala igual, pero para sembrar el pack en un proyecto necesitarás git (https://git-scm.com).")
    os.makedirs(home, exist_ok=True)
    with Candado(home):
        limpiar_restos(home)
        anterior = version_activa(home)
        nueva = instalar_version(home, version)
        if not nueva:
            decir("  La versión {} ya estaba descargada y verificada.".format(version))
        escribir_atomico(os.path.join(home, "actual"), version + "\n")
        registro = leer_registro(home)
        lanzador, archivos = crear_lanzadores(home)
        registro["lanzadores"] = sorted(set(registro.get("lanzadores", []) + archivos))
        registro["python"] = sys.executable
        path_pendiente = con_panel and not sin_path and not en_path(carpeta_bin(home))   # lo decide la persona en el panel
        aviso_path = "" if sin_path or path_pendiente else asegurar_path(home, registro)
        escribir_atomico(os.path.join(home, "instalacion.json"), json.dumps(registro, indent=2, ensure_ascii=True) + "\n")
        podar_versiones(home, version)
    r = subprocess.run([sys.executable, lanzador, "version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if r.returncode != 0 or version not in r.stdout:
        raise ErrorInstalacion("La herramienta quedó instalada pero no responde:\n" + r.stdout)
    comando = "uxyngraphar" if (ES_WINDOWS or aviso_path or en_path(os.path.dirname(lanzador))) else lanzador
    guardar_bienvenida(home, {"version": version, "anterior": anterior, "lanzador": lanzador, "comando": comando,
                              "path_pendiente": path_pendiente, "sin_path": sin_path})
    if anterior == version:
        decir("\nYa tenías uxyngraphar {}: no hay nada que actualizar.".format(version))
        return 0
    decir("\nListo: uxyngraphar {} {}.".format(version, "activo (antes {})".format(anterior) if anterior else "instalado"))
    if aviso_path:
        decir(aviso_path)
    if anterior:
        decir("Tus proyectos siguen como estaban. Para llevarlos a esta versión:  {} actualizar  (o  {} actualizar --todos)".format(comando, comando))
        return 0
    decir("\nQué sigue:\n  1. Entra en la carpeta de tu proyecto.\n  2. Ejecuta:  {} instalar\n  3. Más adelante, para actualizar:  {} autoactualizar  y luego  {} actualizar".format(comando, comando, comando))
    return 0


def main(argv=None):
    preparar_consola()
    ap = argparse.ArgumentParser(prog="instalar-uxyngraphar", description="Instala o actualiza la herramienta uxyngraphar en este equipo.")
    ap.add_argument("--version", default="", help="versión concreta (X.Y.Z); por defecto la de este instalador")
    ap.add_argument("--sin-path", action="store_true", help="no tocar el PATH ni los archivos de inicio de la terminal")
    ap.add_argument("--consola", action="store_true", help="todo en la terminal: no abrir el panel del navegador al terminar")
    a = ap.parse_args(argv)
    problema = problema_python()
    if problema:
        fallo(problema)
        return 1
    version = (a.version or VERSION).strip().lstrip("v")
    if version.startswith("__"):
        fallo("Esta copia del instalador es la del repositorio y no lleva versión fija: indica una con --version X.Y.Z.")
        return 2
    if not VERSION_RE.match(version):
        fallo("Versión no válida: «{}». Usa el formato X.Y.Z (por ejemplo --version 1.0.0).".format(version))
        return 2
    con_panel = not a.consola and not os.environ.get("UXYNGRAPHAR_CONSOLA") and puede_abrir_panel()
    try:
        codigo = instalar(version, a.sin_path or bool(os.environ.get("UXYNGRAPHAR_SIN_PATH")), con_panel)
        return abrir_panel(carpeta_home()) if codigo == 0 and con_panel else codigo
    except ErrorInstalacion as exc:
        fallo(str(exc))
        return 1
    except KeyboardInterrupt:
        fallo("Cancelado. No quedó nada a medias: la versión anterior (si había) sigue activa.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
