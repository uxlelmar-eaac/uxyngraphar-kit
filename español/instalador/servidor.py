"""Servidor local del asistente: solo escucha en 127.0.0.1, con un token por sesión. Sin dependencias."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import api
import api_acciones as acc
import api_actualizar as act
import api_mover
import api_panel as panel
import api_sistema as sis
import explorar

AQUI = Path(__file__).resolve().parent
EXPLORADOR = AQUI / "explorador.html"   # explorador de carpetas común: se inserta donde la página tiene <!--EXPLORADOR-->
FRAGMENTOS = {"<!--EXPLORADOR-->": EXPLORADOR, "<!--PROYECTO-->": AQUI / "panel_proyecto.html",
              "<!--SISTEMA-->": AQUI / "panel_sistema.html"}   # partes de página que se insertan
ESTADO = {"ultima": time.time(), "despedida": ""}   # última petición (cierre por inactividad en segundo plano) y aviso al cerrar
INACTIVO_FONDO = 4 * 3600   # un panel en segundo plano sin pestaña que lo use se cierra solo
PAGINAS = {"instalar": AQUI / "pagina.html", "actualizar": AQUI / "pagina_actualizar.html", "panel": AQUI / "pagina_panel.html"}


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
    """Las del panel de configuración (uxyngraphar panel). Ruta del proyecto y carpeta del pack llegan en cada petición."""
    def rd(b: dict) -> tuple[str, str]:
        ruta = str(b.get("ruta", ""))
        return ruta, str(b.get("docs") or api.carpeta_pack.resolver(Path(ruta).expanduser() if ruta else "."))
    return {"/api/panel/resumen": lambda b: panel.resumen(), "/api/panel/ultima": lambda b: panel.ultima(), "/api/panel/autoactualizar": lambda b: panel.autoactualizar(),
            "/api/panel/agregar": lambda b: panel.agregar(str(b.get("ruta", ""))), "/api/panel/quitar": lambda b: panel.quitar(str(b.get("ruta", ""))),
            "/api/panel/salud": lambda b: panel.salud(*rd(b)), "/api/panel/ver": lambda b: panel.ver(*rd(b)),
            "/api/panel/previsualizar": lambda b: panel.previsualizar(*rd(b), b.get("cambios") or {}),
            "/api/panel/guardar": lambda b: panel.guardar(*rd(b), b.get("cambios") or {}, str(b.get("huella", ""))),
            "/api/panel/colaborar": lambda b: panel.colaborar(*rd(b), b.get("si") is True, b.get("borrar_remoto") is True),
            "/api/panel/plantilla": lambda b: panel.ver_plantilla(), "/api/panel/plantilla/guardar": lambda b: panel.guardar_plantilla(b.get("plantilla") or {}),
            "/api/panel/plantilla/aplicar": lambda b: panel.plantilla_en(list(b.get("destinos") or []), b.get("aplicar") is True),
            "/api/panel/path": lambda b: panel.decidir_path(b.get("agregar") is True),
            "/api/panel/mover/ver": lambda b: api_mover.ver(*rd(b), str(b.get("a") or "")),
            "/api/panel/mover/aplicar": lambda b: api_mover.aplicar(*rd(b), str(b.get("a") or "")),
            **rutas_acciones(rd)}


def rutas_sistema(apagar) -> dict:
    """La herramienta de este equipo. Reiniciar y desinstalar cierran este servidor cuando han respondido."""
    def cerrando(r: dict, aviso: str) -> dict:
        if r.get("ok"):
            ESTADO["despedida"] = aviso.format(**r)
            apagar()
        return r
    return {"/api/sistema/info": lambda b: sis.info(), "/api/sistema/usar": lambda b: sis.usar(str(b.get("version") or "")),
            "/api/sistema/path": lambda b: sis.path(b.get("agregar") is True), "/api/sistema/limpiar": lambda b: sis.limpiar(b.get("aplicar") is True),
            "/api/sistema/reiniciar": lambda b: cerrando(sis.reiniciar(), "El panel sigue abierto con la versión {version} en {url}\n(en segundo plano: ciérralo con «Cerrar» en la página)."),
            "/api/sistema/desinstalar": lambda b: cerrando(sis.desinstalar(str(b.get("confirmacion") or "")), "uxyngraphar se desinstaló de este equipo. Tus proyectos no se tocaron.")}


def rutas_acciones(rd) -> dict:
    """Acciones sobre un proyecto (salud, pendientes, copias, memoria, colaboración, protecciones, reglas, orden)."""
    s = lambda b, k: str(b.get(k) or "")   # noqa: E731
    lista = lambda b: [str(x) for x in (b.get("archivos") or [])]   # noqa: E731
    return {"/api/panel/doctor": lambda b: acc.doctor(*rd(b)), "/api/panel/arreglar": lambda b: acc.arreglar(*rd(b)),
            "/api/panel/pendientes": lambda b: acc.pendientes(*rd(b)), "/api/panel/ficha": lambda b: acc.ficha(*rd(b), s(b, "rel")),
            "/api/panel/decision/previa": lambda b: acc.decision_previa(*rd(b), s(b, "id"), s(b, "accion")),
            "/api/panel/decision/aplicar": lambda b: acc.decidir(*rd(b), s(b, "id"), s(b, "accion")),
            "/api/panel/respaldos": lambda b: acc.respaldos(*rd(b)),
            "/api/panel/respaldo/plan": lambda b: acc.respaldo_plan(*rd(b), s(b, "id"), lista(b)),
            "/api/panel/respaldo/diferencia": lambda b: acc.respaldo_diferencia(*rd(b), s(b, "id"), s(b, "rel")),
            "/api/panel/respaldo/restaurar": lambda b: acc.restaurar(*rd(b), s(b, "id"), lista(b)),
            "/api/panel/respaldos/limpiar": lambda b: acc.limpiar_respaldos(*rd(b), b.get("aplicar") is True),
            "/api/panel/memoria": lambda b: acc.memoria(*rd(b), s(b, "orden"), s(b, "id"), s(b, "texto"), s(b, "motivo"), s(b, "confirmar")),
            "/api/panel/feedback": lambda b: acc.feedback(*rd(b), s(b, "orden")),
            "/api/panel/protecciones": lambda b: acc.protecciones(*rd(b)),
            "/api/panel/ganchos": lambda b: acc.ganchos(*rd(b), b.get("quitar") is True, b.get("pre_push") is True),
            "/api/panel/propietario": lambda b: acc.propietario(*rd(b), s(b, "propietario"), b.get("aplicar") is True),
            "/api/panel/reglas": lambda b: acc.reglas(*rd(b)),
            "/api/panel/ordenar": lambda b: acc.ordenar(*rd(b), s(b, "orden"), b.get("dias") if isinstance(b.get("dias"), int) else 0, b.get("aplicar") is True)}


def crear(token: str, apagar, modo: str = "instalar", inicial: list[str] | None = None, bienvenida: bool = False) -> type[BaseHTTPRequestHandler]:
    pagina = PAGINAS[modo]
    rutas = {"/api/inicio": lambda b: {"rutas": inicial or [], "bienvenida": panel.bienvenida() if bienvenida else None}, "/api/act/revisar": lambda b: act.revisar(b.get("rutas", [])),
             "/api/act/diferencia": lambda b: act.diferencia(b.get("repo", ""), b.get("docs", ""), b.get("rel", "")), "/api/act/aplicar": lambda b: act.aplicar(b.get("seleccion", []), str(b.get("colaborar", ""))), "/api/act/colaboracion": lambda b: act.info_colaboracion(),
             "/api/inspeccionar": lambda b: api.inspeccionar(b.get("ruta", "")), "/api/colaboracion": lambda b: api.info_colaboracion(), "/api/plan": api.planificar, "/api/ejecutar": lambda b: panel.registrar_instalados({**api.ejecutar(b), "siguientes": api.siguientes_pasos(b)}) if modo == "panel" else {**api.ejecutar(b), "siguientes": api.siguientes_pasos(b)},
             "/api/carpetas": lambda b: explorar.listar(str(b.get("ruta") or ""), b.get("ocultas") is True), "/api/abrir": lambda b: abrir_carpeta(b.get("ruta", "")), "/api/salir": lambda b: (apagar(), {"ok": True})[1],
             **rutas_panel(), **rutas_sistema(apagar)}

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
            ESTADO["ultima"] = time.time()
            camino = self.path.split("?")[0]
            otra = PAGINAS.get(camino.strip("/")) if modo == "panel" else None   # desde el panel se abren también instalar y actualizar
            if not self._local() or (camino != "/" and otra is None):
                return self._enviar(404, b"No encontrado", "text/plain; charset=utf-8")
            html = (otra or pagina).read_text(encoding="utf-8")
            for marca, archivo in FRAGMENTOS.items():
                if marca in html:
                    html = html.replace(marca, archivo.read_text(encoding="utf-8"))
            html = html.replace("__TOKEN__", token)
            self._enviar(200, html.encode("utf-8"), "text/html; charset=utf-8")

        def do_POST(self):
            ESTADO["ultima"] = time.time()
            if not self._local() or self.headers.get("X-Token") != token or self.path not in rutas:
                return self._enviar(403, b"{}", "application/json")
            try:
                cuerpo = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
                datos = rutas[self.path](cuerpo)
            except Exception as exc:  # noqa: BLE001 - nunca dejar la pantalla colgada
                datos = {"ok": False, "errores": [f"Error inesperado: {exc}"], "destinos": []}
            self._enviar(200, json.dumps(datos, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    return Manejador


def _vigilar_inactividad(servidor: ThreadingHTTPServer) -> None:
    while time.time() - ESTADO["ultima"] < INACTIVO_FONDO:
        time.sleep(60)
    servidor.shutdown()


def servir(abrir: bool = True, modo: str = "instalar", rutas: list[str] | None = None, bienvenida: bool = False, fondo: bool = False) -> int:
    """fondo: arrancado por otro panel (tras actualizar): sin navegador ni consola; escribe su dirección en UXYNGRAPHAR_PANEL_URL."""
    token = secrets.token_urlsafe(16)
    servidor: ThreadingHTTPServer | None = None

    def apagar():
        threading.Thread(target=lambda: servidor.shutdown() if servidor else None, daemon=True).start()

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), crear(token, apagar, modo, rutas, bienvenida))
    servidor.daemon_threads = False   # al cerrar se espera a las respuestas en curso («Cerrar», reiniciar, desinstalar)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    if fondo:
        aviso = os.environ.get("UXYNGRAPHAR_PANEL_URL", "")
        if aviso:
            Path(aviso).write_text(url + "?tab=sistema", encoding="utf-8")
        threading.Thread(target=_vigilar_inactividad, args=(servidor,), daemon=True).start()
    else:
        print(f"{'Panel' if modo == 'panel' else 'Asistente'} de uxyngraphar abierto en tu navegador:\n  {url}\n\nSi no se abrió solo, copia esa dirección en el navegador.\nCuando termines, pulsa «Cerrar» en la página (o Ctrl+C aquí).")
    if abrir and not fondo:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
    if ESTADO["despedida"] and not fondo:
        print("\n" + ESTADO["despedida"])
    return 0
