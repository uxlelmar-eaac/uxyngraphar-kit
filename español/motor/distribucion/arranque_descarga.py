#!/usr/bin/env python3
# Instalador de una linea de uxyngraphar (solo biblioteca estandar, cualquier sistema).
#   Linux/macOS:  curl -fsSL https://github.com/uxlelmar-eaac/uxyngraphar-kit/releases/latest/download/instalar-uxyngraphar.py | python3 -
#   Windows:      irm https://github.com/uxlelmar-eaac/uxyngraphar-kit/releases/latest/download/instalar-uxyngraphar.py | py -
#   Opciones (detras de "python3 -"):  --version X.Y.Z   --sin-path   --consola   --accesos menu,escritorio,barra   --sin-accesos
#                                      --sin-firma (no comprobar la procedencia con gh)   --help
# El archivo publicado es este (descarga y verificacion) + accesos.py (accesos directos) + arranque.py (lanzador, PATH y main), unidos por
# motor/distribucion/publicar.py. Reglas de ambos (las comprueban las pruebas de motor/pruebas/test_instalador.py):
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

REPO = "uxlelmar-eaac/uxyngraphar-kit"
VERSION = "__VERSION__"   # publicar.py la fija al publicar; en el repositorio queda sin fijar
PYTHON_MINIMO = (3, 10)
MARCA = "uxyngraphar-lanzador"
BLOQUE_INI = "# >>> uxyngraphar >>>"
BLOQUE_FIN = "# <<< uxyngraphar <<<"
VERSIONES_GUARDADAS = 3
TAMANO_MAXIMO = 200 * 1024 * 1024
ES_WINDOWS = os.name == "nt"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
LINEA = "uxyngraphar"        # marca de las versiones de esta línea; las del legado (1.0.0-1.2.4 antiguas) no la llevan
FORMATO_MARCA = 1
ARCHIVOS = "ARCHIVOS.sha256"  # huellas de cada archivo de la versión (dentro del zip)
CASA_DATOS = ("proyectos.json", "instalacion.json", "casa.json", "flujos")   # lo que se respalda antes de cambiar de versión
RESPALDOS_CASA = 5
PRIMERA_ATESTADA = (1, 3, 0)  # desde esta versión, cada release lleva atestación de procedencia (actions/attest-build-provenance)
OPCIONES = {"sin_firma": False}   # --sin-firma: no comprobar la procedencia (solo la huella SHA256)


class ErrorInstalacion(Exception):
    pass


PASOS = []  # type: list  # todo lo que se dice en la consola, en texto plano; el panel de bienvenida lo muestra al terminar

# Marcas y colores de la consola (este archivo se publica solo y no puede importar nada del kit).
MARCAS = {"ok": "\u2713", "aviso": "!", "error": "\u2715", "paso": "\u2022"}
MARCAS_ASCII = {"ok": "+", "aviso": "!", "error": "x", "paso": "-"}
COLORES = {"ok": "32", "aviso": "33", "error": "31", "paso": "2", "titulo": "1", "seccion": "1"}


def color_activo(flujo):
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    try:
        if not flujo.isatty():
            return False
    except (AttributeError, ValueError):
        return False
    if ES_WINDOWS:
        try:
            os.system("")   # activa los colores de la consola en Windows 10+  # noqa: S605 - os.system("") sin argumentos: solo activa los colores de la consola de Windows
        except Exception:  # noqa: BLE001
            return False
    return True


def _pintar(texto, tipo, flujo):
    return "\x1b[{}m{}\x1b[0m".format(COLORES[tipo], texto) if texto and color_activo(flujo) else texto


def _marca(tipo, flujo):
    simbolo = MARCAS[tipo]
    try:
        simbolo.encode(getattr(flujo, "encoding", None) or "utf-8")
    except (UnicodeEncodeError, LookupError):
        simbolo = MARCAS_ASCII[tipo]
    return _pintar(simbolo, tipo, flujo)


def formatear(texto, tipo, flujo):
    """Respeta los saltos y la sangría del texto; pone la marca delante y colorea la primera línea."""
    if not tipo:
        return texto
    cuerpo = texto.lstrip("\n ")
    prefijo = texto[:len(texto) - len(cuerpo)]
    primera, _, resto = cuerpo.partition("\n")
    if tipo in MARCAS:
        color = _pintar(primera, tipo, flujo) if tipo in ("error", "aviso") else primera
        primera = _marca(tipo, flujo) + " " + color
    else:
        primera = _pintar(primera, tipo, flujo)
    return prefijo + primera + ("\n" + resto if resto else "")


def decir(texto="", tipo=""):
    """Escribe en la consola. tipo: ok, aviso, paso (con marca) o titulo, seccion (resaltado)."""
    PASOS.append(texto)
    print(formatear(texto, tipo, sys.stdout), flush=True)


def fallo(texto):
    PASOS.append("ERROR: " + texto)
    print("\n" + formatear("ERROR: " + texto, "error", sys.stderr), file=sys.stderr, flush=True)


def preparar_consola():
    for flujo in (sys.stdout, sys.stderr):
        reconfigurar = getattr(flujo, "reconfigure", None)
        try:
            if reconfigurar is not None:
                reconfigurar(errors="replace")
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


def home_propio():
    """True si UXYNGRAPHAR_HOME cambia la carpeta base y no hay UXYNGRAPHAR_BIN que diga dónde va el comando."""
    return bool(os.environ.get("UXYNGRAPHAR_HOME")) and not os.environ.get("UXYNGRAPHAR_BIN")


def carpeta_bin(home):
    # Con una carpeta base propia (pruebas, instalaciones aparte) el comando va dentro de ella:
    # así nunca pisa el ~/.local/bin de la instalación normal ni deja un comando que apunte a una carpeta temporal.
    if ES_WINDOWS or home_propio():
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
    r = subprocess.run([curl, "-fsSL", "--max-time", str(espera), "-o", destino, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: PLW1510 - el código de salida se lee aparte
    return r.returncode == 0


def descargar(url, destino, intentos=3, espera=60):
    ultimo = None  # type: Exception | None
    for n in range(intentos):
        try:
            peticion = urllib.request.Request(url, headers={"User-Agent": "uxyngraphar-instalador"})  # noqa: S310 - URL https fija del propio kit o de 127.0.0.1
            with urllib.request.urlopen(peticion, timeout=espera) as r, open(destino, "wb") as f:  # noqa: S310 - URL https fija del propio kit o de 127.0.0.1
                shutil.copyfileobj(r, f)
            return
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise ErrorInstalacion("No existe {} (404). Comprueba que esa versión esté publicada y que el repositorio sea público.".format(url)) from None
            ultimo = exc
        except (urllib.error.URLError, OSError) as exc:
            if _es_error_certificado(exc):
                if _descargar_con_curl(url, destino, espera):
                    return
                raise ErrorInstalacion("Python no puede verificar los certificados HTTPS. En macOS ejecuta «Install Certificates.command» "
                                       "(carpeta Aplicaciones > Python 3.x) y repite el comando.") from None
            ultimo = exc
        if n + 1 < intentos:
            time.sleep(n + 1)
    raise ErrorInstalacion("No pude descargar {} ({}). Revisa tu conexión o el proxy (variable HTTPS_PROXY) y vuelve a intentarlo.".format(url, ultimo))


def _gh_no_disponible(salida):
    """gh está, pero no puede consultar a GitHub (sin sesión, sin red): no es una prueba de que la descarga sea mala."""
    texto = salida.lower()
    return any(s in texto for s in ("gh auth login", "authentication", "http 401", "http 403", "could not resolve",
                                    "connection", "timeout", "network", "rate limit", "no such host", "dial tcp"))


def verificar_procedencia(ruta, version):
    """Comprueba con `gh attestation verify` que el archivo lo construyó el workflow del repositorio del kit. True si
    queda verificada; False (con aviso) si no se puede comprobar; ErrorInstalacion si gh dice que no corresponde."""
    if os.environ.get("UXYNGRAPHAR_URL_BASE"):
        decir("  Aviso: descarga desde UXYNGRAPHAR_URL_BASE, no desde las releases de GitHub: no compruebo la procedencia.", "aviso")
        return False
    if clave_version(version) < PRIMERA_ATESTADA:
        decir("  La versión {} se publicó antes de las atestaciones de procedencia: solo se comprueba su huella SHA256.".format(version), "aviso")
        return False
    if OPCIONES["sin_firma"] or os.environ.get("UXYNGRAPHAR_SIN_FIRMA") == "1":
        decir("  Aviso: --sin-firma: no compruebo la procedencia, solo la huella SHA256.", "aviso")
        return False
    gh = shutil.which("gh")
    if not gh:
        decir("  Aviso: sin la CLI de GitHub (gh) no puedo comprobar la procedencia de la descarga; solo su huella SHA256. "
              "Para la vía verificable, ver SECURITY.md del kit.", "aviso")
        return False
    try:
        r = subprocess.run([gh, "attestation", "verify", ruta, "--repo", REPO], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           universal_newlines=True, errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        decir("  Aviso: no pude ejecutar gh para comprobar la procedencia ({}); solo la huella SHA256.".format(exc), "aviso")
        return False
    if r.returncode == 0:
        decir("  Procedencia verificada: lo construyó el workflow de {}.".format(REPO), "ok")
        return True
    if _gh_no_disponible(r.stdout):
        decir("  Aviso: gh no pudo consultar a GitHub (¿sin sesión o sin red?); solo compruebo la huella SHA256.", "aviso")
        return False
    raise ErrorInstalacion("La atestación de procedencia de {} no corresponde a {}; no instalo nada.\n{}\n"
                           "Si sabes lo que haces, --sin-firma instala sin comprobarla.".format(os.path.basename(ruta), REPO, r.stdout.strip()[-1500:]))


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
            raise ErrorInstalacion("El sistema descomprimido es demasiado grande; no lo instalo.")
        for info in infos:
            enlace = (info.external_attr >> 16) & 0o170000 == 0o120000
            if not ruta_segura(info.filename, prefijo) or enlace:
                raise ErrorInstalacion("El sistema contiene una ruta no permitida ({}); no instalo nada.".format(info.filename))
        for info in infos:
            rel = info.filename[len(prefijo):]
            if not rel or info.filename.endswith("/"):
                continue
            dst = os.path.join(destino, *rel.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with z.open(info) as origen, open(dst, "wb") as salida:
                shutil.copyfileobj(origen, salida)


def leer_huellas(ruta):
    huellas = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            partes = linea.rstrip("\n").split("  ", 1)
            if len(partes) == 2 and re.match(r"^[0-9a-f]{64}$", partes[0]):
                huellas[partes[1]] = partes[0]
    return huellas


def archivos_alterados(carpeta):
    """Archivos de ARCHIVOS.sha256 que faltan o cambiaron. None si la versión no trae la lista."""
    lista = os.path.join(carpeta, ARCHIVOS)
    if not os.path.isfile(lista):
        return None
    malos = []
    for rel, huella in sorted(leer_huellas(lista).items()):
        ruta = os.path.join(carpeta, *rel.split("/"))
        if not os.path.isfile(ruta) or sha256(ruta) != huella:
            malos.append(rel)
    return malos


def comprobar_contenido(carpeta, version):
    for rel in ("motor/uxyngraphar.py", "motor/VERSION", "motor/cli.py", "motor/distribucion/arranque.py", ARCHIVOS):
        if not os.path.isfile(os.path.join(carpeta, *rel.split("/"))):
            raise ErrorInstalacion("Al sistema le falta {}; no lo instalo.".format(rel))
    with open(os.path.join(carpeta, "motor", "VERSION"), encoding="utf-8") as f:
        dice = f.read().strip()
    if dice != version:
        raise ErrorInstalacion("El sistema dice ser la versión {} y se esperaba {}; no lo instalo.".format(dice or "?", version))
    malos = archivos_alterados(carpeta)
    if malos:
        raise ErrorInstalacion("El sistema no coincide con su lista de huellas ({}); no lo instalo.".format(", ".join(malos[:5])))


def leer_marca(carpeta):
    """La marca de una versión completa de esta línea, o None (incompleta, dañada o del legado)."""
    try:
        with open(os.path.join(carpeta, ".completa"), encoding="utf-8") as f:
            marca = json.loads(f.read())
    except (OSError, ValueError):
        return None
    if not isinstance(marca, dict) or marca.get("linea") != LINEA or marca.get("version") != os.path.basename(carpeta):
        return None
    if not os.path.isfile(os.path.join(carpeta, "motor", "uxyngraphar.py")):
        return None
    return marca


def version_completa(carpeta):
    return leer_marca(carpeta) is not None


def es_legado(carpeta):
    """Carpeta de una versión del legado (instalada por los instaladores 1.0.0-1.2.4 antiguos)."""
    if os.path.isfile(os.path.join(carpeta, "motor", "uxyngraphar.py")):
        return False
    return os.path.isfile(os.path.join(carpeta, ".completa")) or os.path.isfile(os.path.join(carpeta, "uxyngraphar.py"))


def clave_version(v):
    return tuple(int(x) for x in v.split("."))


def versiones_guardadas(home):
    raiz = os.path.join(home, "versiones")
    if not os.path.isdir(raiz):
        return []
    lista = [v for v in os.listdir(raiz) if VERSION_RE.match(v) and version_completa(os.path.join(raiz, v))]
    return sorted(lista, key=clave_version)


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


def apartar_legado(home):
    """Mueve las versiones del legado de versiones/ a legado/: así nunca se activan ni chocan con números nuevos.
    Devuelve [(origen, destino)] para poder deshacerlo si la instalación falla."""
    raiz = os.path.join(home, "versiones")
    movidas = []
    for nombre in sorted(os.listdir(raiz)) if os.path.isdir(raiz) else []:
        origen = os.path.join(raiz, nombre)
        if not (VERSION_RE.match(nombre) and os.path.isdir(origen) and es_legado(origen)):
            continue
        destino = os.path.join(home, "legado", nombre)
        n = 1
        while os.path.exists(destino):
            n += 1
            destino = os.path.join(home, "legado", "{}-{}".format(nombre, n))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        try:
            shutil.move(origen, destino)
        except OSError:
            continue
        movidas.append((origen, destino))
    if movidas:
        decir("  Versiones del legado apartadas en {}: {}.".format(os.path.join(home, "legado"),
                                                                ", ".join(os.path.basename(o) for o, _ in movidas)), "paso")
    return movidas


def devolver_legado(movidas):
    for origen, destino in reversed(movidas):
        if os.path.isdir(destino) and not os.path.exists(origen):
            try:
                shutil.move(destino, origen)
            except OSError:
                pass


def limpiar_restos(home):
    raiz = os.path.join(home, "versiones")
    for nombre in os.listdir(raiz) if os.path.isdir(raiz) else []:
        ruta = os.path.join(raiz, nombre)
        if nombre.endswith((".tmp", ".viejo")) or (VERSION_RE.match(nombre) and not version_completa(ruta) and not es_legado(ruta)):
            shutil.rmtree(ruta, ignore_errors=True)
    for nombre in os.listdir(home):
        if nombre.startswith(".descarga-"):
            shutil.rmtree(os.path.join(home, nombre), ignore_errors=True)


def entorno_motor(home):
    return dict(os.environ, UXYNGRAPHAR_HOME=home, UXYNGRAPHAR_BIN=os.environ.get("UXYNGRAPHAR_BIN") or carpeta_bin(home),
                PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")


def ejecutar_motor(carpeta, home, *args):
    """Ejecuta motor/uxyngraphar.py de una versión concreta. Devuelve (código, salida)."""
    cli = os.path.join(carpeta, "motor", "uxyngraphar.py")
    try:
        r = subprocess.run([sys.executable, cli] + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL, env=entorno_motor(home), timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def prueba_de_humo(carpeta, home, version):
    """La versión arranca, importa todos sus módulos y su catálogo valida, sin tocar nada de la casa."""
    codigo, salida = ejecutar_motor(carpeta, home, "_autocomprobar")
    if codigo != 0 or ("ok " + version) not in salida:
        raise ErrorInstalacion("La versión {} no pasa su comprobación de arranque; no la activo:\n{}".format(version, salida.strip()[-2000:]))


def instalar_version(home, version, forzar=False):
    """Descarga, verifica, prueba y deja lista versiones/X.Y.Z. False si ya estaba completa (y no se fuerza)."""
    final = os.path.join(home, "versiones", version)
    if version_completa(final) and not forzar:
        return False
    os.makedirs(os.path.dirname(final), exist_ok=True)
    trabajo = tempfile.mkdtemp(prefix=".descarga-", dir=home)
    tmp = final + ".tmp"
    try:
        nombre_zip = "uxyngraphar-{}.zip".format(version)
        decir("  Descargando la versión {}...".format(version), "paso")
        ruta_sumas = os.path.join(trabajo, "SHA256SUMS")
        descargar(url_de(version, "SHA256SUMS"), ruta_sumas)
        sumas = leer_sumas(ruta_sumas)
        if nombre_zip not in sumas:
            raise ErrorInstalacion("La lista de huellas (SHA256SUMS) no incluye {}; no instalo nada.".format(nombre_zip))
        ruta_zip = os.path.join(trabajo, nombre_zip)
        descargar(url_de(version, nombre_zip), ruta_zip)
        if sha256(ruta_zip) != sumas[nombre_zip]:
            raise ErrorInstalacion("La descarga no coincide con su huella SHA256; no instalo nada. Vuelve a intentarlo y, si se repite, avísalo en el repositorio.")
        decir("  Huella SHA256 verificada.", "ok")
        verificar_procedencia(ruta_zip, version)
        try:
            extraer_seguro(ruta_zip, tmp, "uxyngraphar-{}/".format(version))
        except zipfile.BadZipFile:
            raise ErrorInstalacion("El sistema descargado está dañado; no instalo nada.") from None
        comprobar_contenido(tmp, version)
        prueba_de_humo(tmp, home, version)
        decir("  Comprobación de arranque superada.", "ok")
        marca = {"linea": LINEA, "formato": FORMATO_MARCA, "version": version, "sha256": sumas[nombre_zip],
                 "instalada": time.strftime("%Y-%m-%dT%H:%M:%S")}
        escribir_atomico(os.path.join(tmp, ".completa"), json.dumps(marca, indent=2) + "\n")
        viejo = final + ".viejo"
        if os.path.exists(final):
            shutil.rmtree(viejo, ignore_errors=True)
            os.replace(final, viejo)
        try:
            os.replace(tmp, final)
        except OSError:
            if os.path.exists(viejo) and not os.path.exists(final):
                os.replace(viejo, final)
            raise
        shutil.rmtree(viejo, ignore_errors=True)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)
    return True


def podar_versiones(home, protegidas):
    """Deja como mucho VERSIONES_GUARDADAS versiones; nunca borra las protegidas (activa, anterior, última buena)."""
    protegidas = set(v for v in protegidas if v)
    candidatas = [v for v in versiones_guardadas(home) if v not in protegidas]
    sobran = max(0, len(candidatas) + len(protegidas) - VERSIONES_GUARDADAS)
    for v in candidatas[:sobran]:
        shutil.rmtree(os.path.join(home, "versiones", v), ignore_errors=True)


def respaldar_casa(home):
    """Copia los datos de la casa (proyectos, registro, flujos guardados) a respaldos/casa-<fecha>/. Devuelve la carpeta."""
    destino = os.path.join(home, "respaldos", "casa-" + time.strftime("%Y%m%d-%H%M%S"))
    n = 1
    while os.path.exists(destino):
        n += 1
        destino = destino.rsplit("~", 1)[0] + "~{}".format(n)
    os.makedirs(destino)
    for nombre in CASA_DATOS:
        origen = os.path.join(home, nombre)
        if os.path.isdir(origen):
            shutil.copytree(origen, os.path.join(destino, nombre))
        elif os.path.isfile(origen):
            shutil.copy2(origen, os.path.join(destino, nombre))
    escribir_atomico(os.path.join(destino, ".completo"), "\n")
    raiz = os.path.dirname(destino)
    viejos = sorted(d for d in os.listdir(raiz) if d.startswith("casa-"))
    for d in viejos[:max(0, len(viejos) - RESPALDOS_CASA)]:
        shutil.rmtree(os.path.join(raiz, d), ignore_errors=True)
    return destino


def restaurar_casa(home, respaldo):
    """Devuelve la casa al estado del respaldo (solo los datos de CASA_DATOS)."""
    if not respaldo or not os.path.isfile(os.path.join(respaldo, ".completo")):
        return False
    for nombre in CASA_DATOS:
        actual = os.path.join(home, nombre)
        guardado = os.path.join(respaldo, nombre)
        if os.path.isdir(actual):
            shutil.rmtree(actual, ignore_errors=True)
        elif os.path.isfile(actual):
            os.remove(actual)
        if os.path.isdir(guardado):
            shutil.copytree(guardado, actual)
        elif os.path.isfile(guardado):
            shutil.copy2(guardado, actual)
    return True
