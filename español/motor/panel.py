"""Servidor del panel de uxyngraphar: sirve `web/` y la API de `rutas_panel.py`.

Solo escucha en 127.0.0.1. La URL que se abre lleva un código de un solo uso (caduca a los CODIGO_SEGUNDOS) que la página
canjea por una cookie HttpOnly y SameSite=Strict; el token de `panel.json` queda solo para la CLI (cabecera X-Uxyn-Token).
Rechaza un Host que no sea 127.0.0.1 o localhost (DNS rebinding) y un Origin ajeno en los POST, y envía CSP en todas las
respuestas. Hay un solo panel por equipo
(`panel.json` en la carpeta de uxyngraphar): si ya hay uno abierto, se reabre en el navegador. Se cierra solo cuando
ninguna pestaña lo usa durante INACTIVIDAD segundos, y libera el puerto.
"""

from __future__ import annotations

import json
import os
import secrets
import socketserver
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from http.cookies import CookieError, SimpleCookie
from urllib.parse import parse_qs, unquote, urlparse

import auditoria
import casa
import procesos
import rutas_panel

WEB = Path(__file__).resolve().parent / "web"
ESTADO = "panel.json"
INACTIVIDAD = 120
MAX_CUERPO = 1024 * 1024
CODIGO_SEGUNDOS = 60
COOKIE = "uxyn_sesion"
CABECERAS_SEGURIDAD = {
    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Cache-Control": "no-store",
}
REGISTRO_ERRORES = "registros/panel.log"
MAX_REGISTRO = 512 * 1024
TIPOS = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
         ".svg": "image/svg+xml", ".png": "image/png", ".json": "application/json; charset=utf-8", ".ico": "image/x-icon"}


def _codigo_y_mensaje(e: BaseException) -> tuple[str, str, str]:
    codigo, accion = rutas_panel.codigo_error(e)
    return codigo, str(e).strip("'\""), accion


def registrar_error(contexto: str) -> str:
    """Anota la excepción en curso (con su traceback) en registros/panel.log de la carpeta de uxyngraphar; al pasar de
    MAX_REGISTRO, el registro anterior pasa a panel.log.1. Devuelve la ruta del registro."""
    import traceback
    ruta = casa.carpeta() / REGISTRO_ERRORES
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        if ruta.is_file() and ruta.stat().st_size > MAX_REGISTRO:
            os.replace(ruta, ruta.with_name(ruta.name + ".1"))
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} {contexto}\n{traceback.format_exc()}\n")
    except OSError:
        pass
    return str(ruta)


def estatico(ruta_url: str) -> Path | None:
    """Archivo de `web/` para la ruta pedida; None si no existe o intenta salirse de `web/`."""
    rel = unquote(ruta_url).lstrip("/") or "index.html"
    destino = (WEB / rel).resolve()
    if WEB.resolve() not in destino.parents or not destino.is_file() or destino.suffix not in TIPOS:
        return None
    return destino


def manejador(servidor_ref: dict):
    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def _responder(self, codigo: int, cuerpo: bytes, tipo: str = "application/json; charset=utf-8",
                       extra: dict | None = None) -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            for clave, valor in {**CABECERAS_SEGURIDAD, **(extra or {})}.items():
                self.send_header(clave, valor)
            self.end_headers()
            self.wfile.write(cuerpo)

        def _json(self, codigo: int, datos, extra: dict | None = None) -> None:
            self._responder(codigo, json.dumps(datos, ensure_ascii=False, default=str).encode("utf-8"), extra=extra)

        def _error(self, estado: int, codigo: str, mensaje: str, accion: str = "", **mas) -> None:
            """Todos los errores de la API: {"error": {codigo, mensaje, accion}} (M-25)."""
            self._json(estado, {"error": {"codigo": codigo, "mensaje": mensaje, "accion": accion}, **mas})

        def _host_valido(self) -> bool:
            puerto = servidor_ref["servidor"].server_address[1]
            return (self.headers.get("Host") or "") in (f"127.0.0.1:{puerto}", f"localhost:{puerto}")

        def _origen_valido(self) -> bool:
            origen = self.headers.get("Origin")
            puerto = servidor_ref["servidor"].server_address[1]
            return origen is None or origen in (f"http://127.0.0.1:{puerto}", f"http://localhost:{puerto}")

        def _autorizado(self) -> bool:
            srv = servidor_ref["servidor"]
            token = self.headers.get("X-Uxyn-Token")
            if token is not None:
                return secrets.compare_digest(token.encode("utf-8"), srv.token.encode("utf-8"))
            galleta: SimpleCookie = SimpleCookie()
            try:
                galleta.load(self.headers.get("Cookie") or "")
            except CookieError:
                return False
            valor = galleta[COOKIE].value if COOKIE in galleta else ""
            return bool(valor) and secrets.compare_digest(valor.encode("utf-8"), srv.sesion_web.encode("utf-8"))

        def _canjear(self, datos: dict) -> None:
            srv = servidor_ref["servidor"]
            if not srv.canjear(str(datos.get("codigo") or "")):
                return self._error(403, "codigo_caducado", "código caducado o ya usado: abre el panel de nuevo con el comando uxyngraphar", "abrir_de_nuevo")
            galleta = f"{COOKIE}={srv.sesion_web}; HttpOnly; SameSite=Strict; Path=/"
            return self._json(200, {"ok": True}, {"Set-Cookie": galleta})

        def _api(self, metodo: str, datos: dict) -> None:
            srv = servidor_ref["servidor"]
            ruta = urlparse(self.path).path
            if metodo == "POST" and ruta == "/api/canjear":
                return self._canjear(datos)
            if not self._autorizado():
                return self._error(403, "sin_sesion", "token inválido", "abrir_de_nuevo")
            srv.latido = time.time()
            propias = {"GET /api/sesion": lambda d: srv.sesion(), "POST /api/latido": lambda d: True,
                       "POST /api/codigo": lambda d: {"codigo": srv.nuevo_codigo()},
                       "POST /api/cerrar": lambda d: srv.cerrar(), "POST /api/reiniciar": lambda d: srv.cerrar(reiniciar=True)}
            funcion = propias.get(f"{metodo} {ruta}") or (rutas_panel.GET if metodo == "GET" else rutas_panel.POST).get(ruta)
            if not funcion:
                return self._error(404, "ruta_desconocida", "ruta desconocida")
            accion = str(rutas_panel.AUDITADAS.get(ruta) or "") if metodo == "POST" and not datos.get("simular") else ""
            def auditar(error: str = "") -> None:
                if accion:
                    ids = datos.get("ids") or ([datos["id"]] if isinstance(datos.get("id"), str) else [])
                    auditoria.registrar(accion, str(datos.get("repo") or ""), list(ids) if isinstance(ids, list) else [], error=error,
                                        **({"repos": datos["repos"]} if isinstance(datos.get("repos"), list) else {}))
            try:
                resultado = funcion(datos)
            except rutas_panel.ERRORES_CONFLICTO as e:
                auditar(str(e))
                return self._error(409, *_codigo_y_mensaje(e))
            except rutas_panel.ERRORES_USUARIO as e:
                auditar(str(e))
                return self._error(400, *_codigo_y_mensaje(e))
            except Exception as e:  # noqa: BLE001 - un fallo no previsto responde 500 con JSON y queda en el registro
                auditar(f"{type(e).__name__}: {e}")
                registro = registrar_error(f"{metodo} {ruta}")
                return self._error(500, "error_interno", "error interno", "ver_registro", detalle=f"{type(e).__name__}: {e}", registro=registro)
            auditar()
            self._json(200, {"ok": resultado})
            if ruta == "/api/herramienta/desinstalar" and not datos.get("simular") and datos.get("alcance") in ("todo", "herramienta", None):
                srv.cerrar()   # la herramienta ya no está: el panel se apaga y libera el puerto

        def do_GET(self):  # noqa: N802
            if not self._host_valido():
                return self._error(403, "host_no_permitido", "Host no permitido")
            url = urlparse(self.path)
            if url.path.startswith("/api/"):
                return self._api("GET", {k: v[0] for k, v in parse_qs(url.query).items()})
            archivo = estatico(url.path)
            if not archivo:
                return self._responder(404, b"no encontrado", "text/plain; charset=utf-8")
            self._responder(200, archivo.read_bytes(), TIPOS[archivo.suffix])

        def do_POST(self):  # noqa: N802
            if not self._host_valido() or not self._origen_valido():
                self.close_connection = True
                return self._error(403, "origen_no_permitido", "Host u Origin no permitido")
            texto = (self.headers.get("Content-Length") or "0").strip()
            if not texto.isdigit():   # ni negativo ni no numérico: con -1 se leería hasta el final de la conexión
                self.close_connection = True
                return self._error(400, "content_length_invalido", "Content-Length no válido")
            largo = int(texto)
            if largo > MAX_CUERPO:
                self.close_connection = True
                return self._error(413, "pedido_demasiado_grande", f"pedido demasiado grande (máximo {MAX_CUERPO // 1024} KiB)")
            try:
                datos = json.loads(self.rfile.read(largo) or b"{}")
            except ValueError:
                return self._error(400, "json_invalido", "JSON inválido")
            self._api("POST", datos if isinstance(datos, dict) else {})

    return Manejador


class Servidor(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, puerto: int, token: str, bienvenida: bool = False, inactividad: int | None = INACTIVIDAD,
                 sesion_web: str | None = None):
        ref: dict = {}
        super().__init__(("127.0.0.1", puerto), manejador(ref))
        ref["servidor"] = self
        self.token, self.bienvenida, self.inactividad = token, bienvenida, inactividad
        self.sesion_web = sesion_web or secrets.token_urlsafe(32)   # valor de la cookie de las pestañas
        self.codigos: dict[str, float] = {}
        self._candado_codigos = threading.Lock()
        self.latido = time.time()
        self.reiniciar = False

    def server_bind(self) -> None:
        # HTTPServer.server_bind resuelve el nombre del equipo (getfqdn) y en macOS, fuera de la terminal, se cuelga.
        socketserver.TCPServer.server_bind(self)
        host, puerto = self.server_address[:2]
        self.server_name, self.server_port = str(host), int(puerto)

    def nuevo_codigo(self) -> str:
        """Código de un solo uso para abrir el panel en una pestaña; caduca a los CODIGO_SEGUNDOS."""
        codigo = secrets.token_urlsafe(18)
        with self._candado_codigos:
            ahora = time.time()
            self.codigos = {c: t for c, t in self.codigos.items() if t > ahora}
            self.codigos[codigo] = ahora + CODIGO_SEGUNDOS
        return codigo

    def canjear(self, codigo: str) -> bool:
        with self._candado_codigos:
            caduca = self.codigos.pop(codigo, 0.0)
        return caduca > time.time()

    @property
    def url(self) -> str:
        """URL para una pestaña nueva (cada llamada da un código nuevo)."""
        return f"http://127.0.0.1:{self.server_address[1]}/#c={self.nuevo_codigo()}"

    def sesion(self) -> dict:
        return {"bienvenida": self.bienvenida, "inactividad": self.inactividad, "pid": os.getpid(), **rutas_panel.version()}

    def cerrar(self, reiniciar: bool = False) -> bool:
        self.reiniciar = reiniciar
        threading.Timer(0.3, self.shutdown).start()
        return True

    def vigilar(self) -> None:
        """Apaga el servidor cuando ninguna pestaña manda latidos durante `inactividad` segundos."""
        def bucle():
            while self.inactividad:
                time.sleep(min(5, self.inactividad))
                if time.time() - self.latido > self.inactividad:
                    print("Panel cerrado: ninguna pestaña lo usa.")
                    self.shutdown()
                    return
        threading.Thread(target=bucle, daemon=True).start()


def crear_servidor(puerto: int = 0, token: str | None = None, bienvenida: bool = False,
                   inactividad: int | None = INACTIVIDAD, sesion_web: str | None = None) -> tuple[Servidor, str]:
    token = token or secrets.token_urlsafe(24)
    return Servidor(puerto, token, bienvenida, inactividad, sesion_web), token


def url_con_codigo(abierto: dict, bienvenida: bool = False) -> str:
    """URL de una pestaña nueva para el panel ya abierto: le pide un código de un solo uso con el token de panel.json."""
    pedido = urllib.request.Request(f"http://127.0.0.1:{abierto['puerto']}/api/codigo", data=b"{}", method="POST",
                                    headers={"X-Uxyn-Token": abierto["token"], "Content-Type": "application/json"})
    with urllib.request.urlopen(pedido, timeout=3) as r:  # noqa: S310 - URL fija de 127.0.0.1
        codigo = json.loads(r.read())["ok"]["codigo"]
    return f"http://127.0.0.1:{abierto['puerto']}/#c={codigo}" + ("&bienvenida=1" if bienvenida else "")


vivo = procesos.vivo
_vivo = vivo   # nombre anterior


def panel_abierto() -> dict | None:
    """El panel que ya está escuchando en este equipo (puerto, token, pid) o None."""
    datos = casa.leer_json(ESTADO, None)
    if not isinstance(datos, dict) or not vivo(datos.get("pid")):
        return None
    try:
        pedido = urllib.request.Request(f"http://127.0.0.1:{datos['puerto']}/api/sesion", headers={"X-Uxyn-Token": datos["token"]})
        with urllib.request.urlopen(pedido, timeout=2) as r:  # noqa: S310 - URL fija de 127.0.0.1
            return datos if r.status == 200 else None
    except (OSError, ValueError, KeyError):
        return None


def _olvidar_estado(pid: int) -> None:
    datos = casa.leer_json(ESTADO, None)
    if isinstance(datos, dict) and datos.get("pid") == pid:
        (casa.carpeta() / ESTADO).unlink(missing_ok=True)


def _abrir(url: str) -> None:
    threading.Timer(0.3, lambda: webbrowser.open(url)).start()


def _reiniciar(puerto: int, token: str, sesion_web: str) -> int:
    """Arranca de nuevo el panel con la versión activa (tras actualizar), en el mismo puerto, con el mismo token y la
    misma sesión de las pestañas (que siguen funcionando sin volver a abrirse)."""
    lanzador = rutas_panel.herramienta.lanzador() if rutas_panel.herramienta.instalada() else ""
    orden = [sys.executable, lanzador] if lanzador else [sys.executable, str(Path(__file__).resolve().parent / "uxyngraphar.py")]
    env = dict(os.environ, UXYNGRAPHAR_PANEL_TOKEN=token, UXYNGRAPHAR_PANEL_SESION=sesion_web)
    return subprocess.call([*orden, "panel", "--no-abrir", "--puerto", str(puerto)], env=env)


def _reabrir(abierto: dict, abrir: bool, bienvenida: bool) -> int:
    try:
        url = url_con_codigo(abierto, bienvenida)
    except (OSError, ValueError, KeyError):
        print("El panel está abierto pero no responde; ciérralo con «uxyngraphar panel --cerrar».", file=sys.stderr)
        return 1
    print(f"El panel ya está abierto en {url}")
    if abrir:
        webbrowser.open(url)
    return 0


def _desacoplado() -> dict:
    """Opciones de Popen para que el panel siga vivo al cerrar la terminal (y, en Windows, sin ventana de consola)."""
    if os.name != "nt":
        return {"start_new_session": True}
    return {"creationflags": 0x00000008 | 0x00000200}   # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP


def _python_sin_consola() -> str:
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    return str(pythonw) if os.name == "nt" and pythonw.is_file() else sys.executable


def lanzar(puerto: int = 0, abrir: bool = True, bienvenida: bool = False, mantener: bool = False,
           espera: float = 20) -> int:
    """Arranca el panel en su propio proceso, independiente de la terminal, y vuelve en cuanto responde."""
    abierto = panel_abierto()
    if abierto:
        return _reabrir(abierto, abrir, bienvenida)
    orden = [_python_sin_consola(), str(Path(__file__).resolve().parent / "uxyngraphar.py"), "panel", "--primer-plano",
             "--no-abrir", "--puerto", str(puerto)] + (["--bienvenida"] if bienvenida else []) + (["--mantener"] if mantener else [])
    registro = casa.carpeta() / "panel.log"
    registro.parent.mkdir(parents=True, exist_ok=True)
    with open(registro, "ab") as salida:
        proceso = subprocess.Popen(orden, stdin=subprocess.DEVNULL, stdout=salida, stderr=subprocess.STDOUT,
                                   env=dict(os.environ, PYTHONIOENCODING="utf-8"), close_fds=True, **_desacoplado())
    procesos.LANZADOS[proceso.pid] = proceso
    limite = time.time() + espera
    while time.time() < limite:
        abierto = panel_abierto()
        if abierto and abierto.get("pid") == proceso.pid:
            url = url_con_codigo(abierto, bienvenida)
            print(f"Panel uxyngraphar abierto en {url}")
            print("Sigue abierto aunque cierres esta terminal. Para cerrarlo: «Cerrar el panel» en el propio panel o "
                  "`uxyngraphar panel --cerrar`" + ("." if mantener else "; también se cierra solo si no queda ninguna pestaña abierta."))
            if abrir:
                webbrowser.open(url)
            return 0
        if proceso.poll() is not None:
            break
        time.sleep(0.2)
    if proceso.poll() is None:
        proceso.terminate()
        try:
            proceso.wait(5)
        except subprocess.TimeoutExpired:
            proceso.kill()
            proceso.wait(5)
    cola = registro.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-10:]
    print("No pude abrir el panel." + ("\n" + "\n".join(cola) if cola else "") + f"\nRegistro: {registro}", file=sys.stderr)
    return 1


def cerrar_abierto(excepto_pid: int | None = None) -> dict | None:
    """Cierra el panel abierto en este equipo (si no es este mismo proceso). Devuelve el que había, o None."""
    abierto = panel_abierto()
    if not abierto or abierto.get("pid") == (excepto_pid or os.getpid()):
        return None
    try:
        pedido = urllib.request.Request(f"http://127.0.0.1:{abierto['puerto']}/api/cerrar", data=b"{}", method="POST",
                                        headers={"X-Uxyn-Token": abierto["token"], "Content-Type": "application/json"})
        urllib.request.urlopen(pedido, timeout=3).close()  # noqa: S310 - URL fija de 127.0.0.1
    except OSError:
        pass
    for _ in range(20):
        if not vivo(abierto.get("pid")):
            break
        time.sleep(0.2)
    return abierto


def servir(puerto: int = 0, abrir: bool = True, bienvenida: bool = False, mantener: bool = False) -> int:
    abierto = panel_abierto()
    if abierto:
        return _reabrir(abierto, abrir, bienvenida)
    auditoria.ORIGEN["valor"] = "panel"
    servidor, token = crear_servidor(puerto, os.environ.pop("UXYNGRAPHAR_PANEL_TOKEN", None), bienvenida,
                                     None if mantener else INACTIVIDAD, os.environ.pop("UXYNGRAPHAR_PANEL_SESION", None))
    puerto_real = servidor.server_address[1]
    casa.escribir_json(ESTADO, {"puerto": puerto_real, "token": token, "pid": os.getpid()}, privado=True)
    url = servidor.url
    print(f"Panel uxyngraphar en {url}\nCtrl+C para cerrarlo (libera el puerto). "
          + ("" if mantener else "Se cierra solo si no queda ninguna pestaña abierta."), flush=True)
    if abrir:
        _abrir(url)
    servidor.vigilar()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
        _olvidar_estado(os.getpid())
    if servidor.reiniciar:
        return _reiniciar(puerto_real, token, servidor.sesion_web)
    return 0
