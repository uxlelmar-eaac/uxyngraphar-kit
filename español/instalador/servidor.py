"""Servidor local del asistente: solo escucha en 127.0.0.1, con un token por sesión. Sin dependencias."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import api
import api_actualizar as act
import api_panel as panel

AQUI = Path(__file__).resolve().parent
PAGINAS = {"instalar": AQUI / "pagina.html", "actualizar": AQUI / "pagina_actualizar.html", "panel": AQUI / "pagina_panel.html"}
SELECTOR = ("import tkinter as t\nfrom tkinter import filedialog as f\nr=t.Tk();r.withdraw();r.attributes('-topmost',True)\n"
            "print(f.askdirectory(title='Elige la carpeta raíz de tu proyecto'))")


def elegir_carpeta() -> dict:
    try:
        r = subprocess.run([sys.executable, "-c", SELECTOR], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return {"ok": False}
    ruta = r.stdout.strip()
    return {"ok": bool(ruta), "ruta": ruta, "sin_selector": r.returncode != 0}


def abrir_carpeta(ruta: str) -> dict:
    p = Path(ruta)
    if not p.is_dir():
        return {"ok": False}
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(p))  # type: ignore[attr-defined]  # noqa: S606
        else:
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(p)])
    except OSError:
        return {"ok": False}
    return {"ok": True}


def rutas_panel() -> dict:
    """Las del panel de configuración (uxyngraphar panel). Ruta del proyecto y carpeta docs llegan en cada petición."""
    def rd(b: dict) -> tuple[str, str]:
        return str(b.get("ruta", "")), str(b.get("docs", "docs"))
    return {"/api/panel/resumen": lambda b: panel.resumen(), "/api/panel/ultima": lambda b: panel.ultima(),
            "/api/panel/agregar": lambda b: panel.agregar(str(b.get("ruta", ""))), "/api/panel/quitar": lambda b: panel.quitar(str(b.get("ruta", ""))),
            "/api/panel/salud": lambda b: panel.salud(*rd(b)), "/api/panel/ver": lambda b: panel.ver(*rd(b)),
            "/api/panel/previsualizar": lambda b: panel.previsualizar(*rd(b), b.get("cambios") or {}),
            "/api/panel/guardar": lambda b: panel.guardar(*rd(b), b.get("cambios") or {}, str(b.get("huella", ""))),
            "/api/panel/colaborar": lambda b: panel.colaborar(*rd(b), b.get("si") is True, b.get("borrar_remoto") is True),
            "/api/panel/plantilla": lambda b: panel.ver_plantilla(), "/api/panel/plantilla/guardar": lambda b: panel.guardar_plantilla(b.get("plantilla") or {}),
            "/api/panel/plantilla/aplicar": lambda b: panel.plantilla_en(list(b.get("destinos") or []), b.get("aplicar") is True),
            "/api/panel/path": lambda b: panel.decidir_path(b.get("agregar") is True)}


def crear(token: str, apagar, modo: str = "instalar", inicial: list[str] | None = None, bienvenida: bool = False) -> type[BaseHTTPRequestHandler]:
    pagina = PAGINAS[modo]
    rutas = {"/api/inicio": lambda b: {"rutas": inicial or [], "bienvenida": panel.bienvenida() if bienvenida else None}, "/api/act/revisar": lambda b: act.revisar(b.get("rutas", [])),
             "/api/act/diferencia": lambda b: act.diferencia(b.get("repo", ""), b.get("docs", ""), b.get("rel", "")), "/api/act/aplicar": lambda b: act.aplicar(b.get("seleccion", []), str(b.get("colaborar", ""))), "/api/act/colaboracion": lambda b: act.info_colaboracion(),
             "/api/inspeccionar": lambda b: api.inspeccionar(b.get("ruta", "")), "/api/colaboracion": lambda b: api.info_colaboracion(), "/api/plan": api.planificar, "/api/ejecutar": lambda b: panel.registrar_instalados({**api.ejecutar(b), "siguientes": api.siguientes_pasos(b)}) if modo == "panel" else {**api.ejecutar(b), "siguientes": api.siguientes_pasos(b)},
             "/api/carpeta": lambda b: elegir_carpeta(), "/api/abrir": lambda b: abrir_carpeta(b.get("ruta", "")), "/api/salir": lambda b: (apagar(), {"ok": True})[1],
             **rutas_panel()}

    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silencio: la consola del asistente no es para trazas HTTP
            pass

        def _local(self) -> bool:
            host = (self.headers.get("Host") or "").split(":")[0]
            return host in ("127.0.0.1", "localhost")   # evita «DNS rebinding»

        def _enviar(self, codigo: int, cuerpo: bytes, tipo: str) -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)

        def do_GET(self):
            camino = self.path.split("?")[0]
            otra = PAGINAS.get(camino.strip("/")) if modo == "panel" else None   # desde el panel se abren también instalar y actualizar
            if not self._local() or (camino != "/" and otra is None):
                return self._enviar(404, b"No encontrado", "text/plain; charset=utf-8")
            html = (otra or pagina).read_text(encoding="utf-8").replace("__TOKEN__", token)
            self._enviar(200, html.encode("utf-8"), "text/html; charset=utf-8")

        def do_POST(self):
            if not self._local() or self.headers.get("X-Token") != token or self.path not in rutas:
                return self._enviar(403, b"{}", "application/json")
            try:
                cuerpo = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
                datos = rutas[self.path](cuerpo)
            except Exception as exc:  # noqa: BLE001 - nunca dejar la pantalla colgada
                datos = {"ok": False, "errores": [f"Error inesperado: {exc}"], "destinos": []}
            self._enviar(200, json.dumps(datos, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    return Manejador


def servir(abrir: bool = True, modo: str = "instalar", rutas: list[str] | None = None, bienvenida: bool = False) -> int:
    token = secrets.token_urlsafe(16)
    servidor: ThreadingHTTPServer | None = None

    def apagar():
        threading.Thread(target=lambda: servidor.shutdown() if servidor else None, daemon=True).start()

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), crear(token, apagar, modo, rutas, bienvenida))
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    print(f"{'Panel' if modo == 'panel' else 'Asistente'} de uxyngraphar abierto en tu navegador:\n  {url}\n\nSi no se abrió solo, copia esa dirección en el navegador.\nCuando termines, pulsa «Cerrar» en la página (o Ctrl+C aquí).")
    if abrir:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
    return 0
