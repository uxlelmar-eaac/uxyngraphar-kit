#!/usr/bin/env python3
# Instalador de una linea de uxyngraphar (solo biblioteca estandar, cualquier sistema).
#   Linux/macOS:  curl -fsSL https://github.com/uxlelmar-eaac/uxyngraphar/releases/latest/download/instalar-uxyngraphar.py | python3 -
#   Windows:      irm https://github.com/uxlelmar-eaac/uxyngraphar/releases/latest/download/instalar-uxyngraphar.py | py -
#   Opciones (detras de "python3 -"):  --version X.Y.Z   --sin-path   --consola   --help
# El archivo publicado es este (descarga y verificacion) + arranque.py (lanzador, PATH y main), unidos por
# _compartido/publicar.py. Reglas de ambos (las comprueban las pruebas de instalador/test_arranque.py):
#   - Todo el codigo vive en funciones y solo se ejecuta en la ultima linea: si la descarga se corta, no hace nada.
#   - El archivo publicado solo lleva ASCII (publicar.py escribe los acentos como \uXXXX): PowerShell 5.1
#     estropea los acentos al pasar texto por tuberia. Aqui no se usan cadenas r"..." con acentos.
#   - Sintaxis valida en Python 3.6, para poder avisar con claridad si el Python es demasiado viejo.

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

REPO = "uxlelmar-eaac/uxyngraphar"
VERSION = "__VERSION__"   # publicar.py la fija al publicar; en el repositorio queda sin fijar
PYTHON_MINIMO = (3, 10)
MARCA = "uxyngraphar-lanzador"
BLOQUE_INI = "# >>> uxyngraphar >>>"
BLOQUE_FIN = "# <<< uxyngraphar <<<"
VERSIONES_GUARDADAS = 3
TAMANO_MAXIMO = 200 * 1024 * 1024
ES_WINDOWS = os.name == "nt"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


class ErrorInstalacion(Exception):
    pass


PASOS = []   # todo lo que se dice en la consola; el panel de bienvenida lo muestra al terminar


def decir(texto=""):
    PASOS.append(texto)
    print(texto, flush=True)


def fallo(texto):
    PASOS.append("ERROR: " + texto)
    print("\nERROR: " + texto, file=sys.stderr, flush=True)


def preparar_consola():
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def problema_python(info=None):
    """Texto del problema si este Python no sirve; cadena vacía si sirve."""
    v = tuple((info or sys.version_info)[:2])
    if v >= PYTHON_MINIMO:
        return ""
    if sys.platform == "darwin":
        como = "Instala Python 3.12 o superior desde https://www.python.org/downloads/ (o con: brew install python) y repite el comando."
    elif ES_WINDOWS:
        como = "Instala Python desde https://www.python.org/downloads/ (marca «Add python.exe to PATH») y repite el comando."
    else:
        como = "Instala python3.10 o superior con el gestor de paquetes de tu sistema y repite el comando."
    return "uxyngraphar necesita Python 3.10 o superior y este es {}.{}. {}".format(v[0], v[1], como)


def carpeta_home():
    propia = os.environ.get("UXYNGRAPHAR_HOME")
    if propia:
        return os.path.abspath(os.path.expanduser(propia))
    if ES_WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
        return os.path.join(base, "uxyngraphar")
    return os.path.join(os.path.expanduser("~"), ".uxyngraphar")


def carpeta_bin(home):
    if ES_WINDOWS:
        return os.path.join(home, "bin")
    return os.path.abspath(os.path.expanduser(os.environ.get("UXYNGRAPHAR_BIN") or os.path.join("~", ".local", "bin")))


def url_base():
    return os.environ.get("UXYNGRAPHAR_URL_BASE", "https://github.com/" + REPO + "/releases").rstrip("/")


def url_de(version, archivo):
    return "{}/download/v{}/{}".format(url_base(), version, archivo)


def url_ultima(archivo):
    return url_base() + "/latest/download/" + archivo


def _es_error_certificado(exc):
    return "CERTIFICATE_VERIFY_FAILED" in str(exc)


def _descargar_con_curl(url, destino, espera):
    curl = shutil.which("curl")
    if not curl:
        return False
    r = subprocess.run([curl, "-fsSL", "--max-time", str(espera), "-o", destino, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


def descargar(url, destino, intentos=3, espera=60):
    ultimo = None
    for n in range(intentos):
        try:
            peticion = urllib.request.Request(url, headers={"User-Agent": "uxyngraphar-instalador"})
            with urllib.request.urlopen(peticion, timeout=espera) as r, open(destino, "wb") as f:
                shutil.copyfileobj(r, f)
            return
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise ErrorInstalacion("No existe {} (404). Comprueba que esa versión esté publicada y que el repositorio sea público.".format(url))
            ultimo = exc
        except (urllib.error.URLError, OSError) as exc:
            if _es_error_certificado(exc):
                if _descargar_con_curl(url, destino, espera):
                    return
                raise ErrorInstalacion("Python no puede verificar los certificados HTTPS. En macOS ejecuta «Install Certificates.command» "
                                       "(carpeta Aplicaciones > Python 3.x) y repite el comando.")
            ultimo = exc
        if n + 1 < intentos:
            time.sleep(n + 1)
    raise ErrorInstalacion("No pude descargar {} ({}). Revisa tu conexión o el proxy (variable HTTPS_PROXY) y vuelve a intentarlo.".format(url, ultimo))


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def leer_sumas(ruta):
    sumas = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split()
            if len(partes) == 2 and re.match(r"^[0-9a-f]{64}$", partes[0]):
                sumas[partes[1].lstrip("*")] = partes[0]
    return sumas


def version_de_sumas(sumas):
    for nombre in sumas:
        m = re.match(r"^uxyngraphar-(\d+\.\d+\.\d+)\.zip$", nombre)
        if m:
            return m.group(1)
    return ""


def ruta_segura(nombre, prefijo):
    if not nombre.startswith(prefijo) or "\\" in nombre or nombre.startswith("/") or ":" in nombre:
        return False
    partes = nombre.split("/")
    return ".." not in partes and "" not in partes[:-1]


def extraer_seguro(ruta_zip, destino, prefijo):
    with zipfile.ZipFile(ruta_zip) as z:
        infos = z.infolist()
        if sum(i.file_size for i in infos) > TAMANO_MAXIMO:
            raise ErrorInstalacion("El paquete descomprimido es demasiado grande; no lo instalo.")
        for info in infos:
            enlace = (info.external_attr >> 16) & 0o170000 == 0o120000
            if not ruta_segura(info.filename, prefijo) or enlace:
                raise ErrorInstalacion("El paquete contiene una ruta no permitida ({}); no instalo nada.".format(info.filename))
        for info in infos:
            rel = info.filename[len(prefijo):]
            if not rel or info.filename.endswith("/"):
                continue
            dst = os.path.join(destino, *rel.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with z.open(info) as origen, open(dst, "wb") as salida:
                shutil.copyfileobj(origen, salida)


def comprobar_contenido(carpeta, version):
    for rel in ("uxyngraphar.py", "instalar.py", "actualizar.py", "instalador/arranque.py", "backend/VERSION.md", "frontend/VERSION.md"):
        if not os.path.isfile(os.path.join(carpeta, *rel.split("/"))):
            raise ErrorInstalacion("Al paquete le falta {}; no lo instalo.".format(rel))
    with open(os.path.join(carpeta, "backend", "VERSION.md"), encoding="utf-8") as f:
        m = re.search(r"^version:\s*(\S+)", f.read(), re.M)
    if not m or m.group(1) != version:
        raise ErrorInstalacion("El paquete dice ser la versión {} y se esperaba {}; no lo instalo.".format(m.group(1) if m else "?", version))


def version_completa(carpeta):
    return os.path.isfile(os.path.join(carpeta, ".completa"))


def versiones_guardadas(home):
    raiz = os.path.join(home, "versiones")
    if not os.path.isdir(raiz):
        return []
    lista = [v for v in os.listdir(raiz) if VERSION_RE.match(v) and version_completa(os.path.join(raiz, v))]
    return sorted(lista, key=lambda v: tuple(int(x) for x in v.split(".")))


def version_activa(home):
    try:
        with open(os.path.join(home, "actual"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def escribir_atomico(ruta, texto):
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    os.replace(tmp, ruta)


def limpiar_restos(home):
    raiz = os.path.join(home, "versiones")
    for nombre in os.listdir(raiz) if os.path.isdir(raiz) else []:
        ruta = os.path.join(raiz, nombre)
        if nombre.endswith(".tmp") or (VERSION_RE.match(nombre) and not version_completa(ruta)):
            shutil.rmtree(ruta, ignore_errors=True)
    for nombre in os.listdir(home):
        if nombre.startswith(".descarga-"):
            shutil.rmtree(os.path.join(home, nombre), ignore_errors=True)


def instalar_version(home, version):
    """Descarga, verifica y deja lista versiones/X.Y.Z. False si ya estaba completa."""
    final = os.path.join(home, "versiones", version)
    if version_completa(final):
        return False
    os.makedirs(os.path.dirname(final), exist_ok=True)
    trabajo = tempfile.mkdtemp(prefix=".descarga-", dir=home)
    tmp = final + ".tmp"
    try:
        nombre_zip = "uxyngraphar-{}.zip".format(version)
        decir("  Descargando la versión {}...".format(version))
        ruta_sumas = os.path.join(trabajo, "SHA256SUMS")
        descargar(url_de(version, "SHA256SUMS"), ruta_sumas)
        sumas = leer_sumas(ruta_sumas)
        if nombre_zip not in sumas:
            raise ErrorInstalacion("La lista de huellas (SHA256SUMS) no incluye {}; no instalo nada.".format(nombre_zip))
        ruta_zip = os.path.join(trabajo, nombre_zip)
        descargar(url_de(version, nombre_zip), ruta_zip)
        if sha256(ruta_zip) != sumas[nombre_zip]:
            raise ErrorInstalacion("La descarga no coincide con su huella SHA256; no instalo nada. Vuelve a intentarlo y, si se repite, avísalo en el repositorio.")
        decir("  Huella SHA256 verificada.")
        try:
            extraer_seguro(ruta_zip, tmp, "uxyngraphar-{}/".format(version))
        except zipfile.BadZipFile:
            raise ErrorInstalacion("El paquete descargado está dañado; no instalo nada.")
        comprobar_contenido(tmp, version)
        escribir_atomico(os.path.join(tmp, ".completa"), version + "\n")
        if os.path.exists(final):
            shutil.rmtree(final)
        os.replace(tmp, final)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)
    return True


def podar_versiones(home, activa):
    viejas = [v for v in versiones_guardadas(home) if v != activa]
    for v in viejas[:max(0, len(viejas) - (VERSIONES_GUARDADAS - 1))]:
        shutil.rmtree(os.path.join(home, "versiones", v), ignore_errors=True)
