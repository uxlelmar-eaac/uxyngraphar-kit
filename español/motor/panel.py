"""Panel del navegador de uxyngraphar 2.0: catálogo (crear, editar, versionar) y repos (instalar, actualizar, quitar,
verificar, flujo, migrar). Solo escucha en 127.0.0.1 y exige un token por sesión en cada llamada a la API."""

from __future__ import annotations

import json
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import catalogo
import generar
import repo

PAGINA = Path(__file__).resolve().parent / "panel.html"
ERRORES_USUARIO = (ValueError, FileNotFoundError, FileExistsError, PermissionError, KeyError, repo.InstalacionAntigua)


def _raiz(datos: dict) -> Path:
    ruta = Path(str(datos.get("repo") or "")).expanduser()
    if not str(datos.get("repo") or "").strip() or not ruta.is_dir():
        raise ValueError("indica la ruta de un repo existente")
    return ruta.resolve()


def _migrar(datos: dict, aplicar: bool) -> dict:
    from migracion import migrar
    return migrar.ejecutar(_raiz(datos), aplicar=aplicar)


RUTAS_GET = {
    "/api/catalogo": lambda d: catalogo.listar(),
    "/api/catalogo/archivos": lambda d: catalogo.archivos(d["id"]),
    "/api/catalogo/archivo": lambda d: {"contenido": catalogo.leer_archivo(d["id"], d["rel"])},
    "/api/repo/estado": lambda d: {"paquetes": repo.estado(_raiz(d)), "antigua": str(repo.instalacion_1x(_raiz(d)) or "")},
    "/api/repo/flujo": lambda d: (generar.flujo_inicial(_raiz(d)), generar.leer_flujo(_raiz(d)))[1],
    "/api/repo/migrar": lambda d: _migrar(d, aplicar=False),
}
RUTAS_POST = {
    "/api/catalogo/crear": lambda d: str(catalogo.crear(d["id"], d["titulo"], d.get("descripcion", ""))),
    "/api/catalogo/archivo": lambda d: {"errores": catalogo.guardar_archivo(d["id"], d["rel"], d["contenido"])},
    "/api/catalogo/version": lambda d: catalogo.versionar(d["id"], d["nivel"]),
    "/api/repo/instalar": lambda d: repo.instalar(_raiz(d), list(d["ids"])),
    "/api/repo/actualizar": lambda d: repo.actualizar(_raiz(d), list(d.get("ids") or []) or None, forzar=bool(d.get("forzar"))),
    "/api/repo/quitar": lambda d: repo.quitar(_raiz(d), d["id"], bool(d.get("con_trabajo"))),
    "/api/repo/verificar": lambda d: repo.verificar(_raiz(d)),
    "/api/repo/flujo": lambda d: {"errores": generar.guardar_flujo(_raiz(d), d["flujo"])},
    "/api/repo/migrar": lambda d: _migrar(d, aplicar=True),
}


def manejador(token: str):
    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def _responder(self, codigo: int, cuerpo: bytes, tipo: str = "application/json; charset=utf-8") -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)

        def _json(self, codigo: int, datos) -> None:
            self._responder(codigo, json.dumps(datos, ensure_ascii=False, default=str).encode("utf-8"))

        def _api(self, rutas: dict, datos: dict) -> None:
            ruta = urlparse(self.path).path
            if self.headers.get("X-Uxyn-Token") != token:
                return self._json(403, {"error": "token inválido"})
            if ruta not in rutas:
                return self._json(404, {"error": "ruta desconocida"})
            try:
                self._json(200, {"ok": rutas[ruta](datos)})
            except ERRORES_USUARIO as e:
                self._json(400, {"error": str(e)})

        def do_GET(self):  # noqa: N802
            url = urlparse(self.path)
            if url.path == "/":
                return self._responder(200, PAGINA.read_bytes(), "text/html; charset=utf-8")
            self._api(RUTAS_GET, {k: v[0] for k, v in parse_qs(url.query).items()})

        def do_POST(self):  # noqa: N802
            largo = int(self.headers.get("Content-Length") or 0)
            try:
                datos = json.loads(self.rfile.read(largo) or b"{}")
            except ValueError:
                return self._json(400, {"error": "JSON inválido"})
            self._api(RUTAS_POST, datos if isinstance(datos, dict) else {})

    return Manejador


def crear_servidor(puerto: int = 0) -> tuple[ThreadingHTTPServer, str]:
    token = secrets.token_urlsafe(24)
    return ThreadingHTTPServer(("127.0.0.1", puerto), manejador(token)), token


def servir(puerto: int = 0, abrir: bool = True) -> int:
    servidor, token = crear_servidor(puerto)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/#t={token}"
    print(f"Panel uxyngraphar 2.0 en {url}\nCtrl+C para cerrarlo (libera el puerto).")
    if abrir:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
    return 0
