"""Lógica del asistente de instalación (sin interfaz): inspeccionar, planificar y ejecutar. La usan la pantalla web y la consola."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent   # carpeta «español/»: aquí viven instalar.py, actualizar.py y los packs
PACKS = {"servidor": RAIZ / "backend", "cliente": RAIZ / "frontend"}
for _s in (PACKS["servidor"] / "scripts" / "nucleo", PACKS["servidor"] / "scripts" / "control", PACKS["servidor"] / "scripts" / "feedback"):
    if str(_s) not in sys.path:
        sys.path.insert(0, str(_s))

import cliente as feedback  # noqa: E402  (pregunta de colaboración y envío de fichas EVO)
import flujo  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402

TITULOS = {"servidor": "Servidor (API, servicios, workers, CLI, librerías)", "cliente": "Cliente (web, móvil, escritorio)"}
SUGERENCIAS = {"servidor": ("apps/api", "apps/backend", "backend", "api", "server", "services/api"),
               "cliente": ("apps/web", "apps/frontend", "frontend", "web", "client", "apps/app")}


def es_git(carpeta: Path) -> bool:
    try:
        return subprocess.run(["git", "rev-parse", "--git-dir"], cwd=carpeta, capture_output=True).returncode == 0
    except OSError:
        return False


def git_disponible() -> bool:
    try:
        return subprocess.run(["git", "--version"], capture_output=True).returncode == 0
    except OSError:
        return False


def inspeccionar(ruta: str) -> dict:
    """Qué hay en la carpeta elegida: existe, git, pila y packs ya instalados."""
    if not ruta.strip():
        return {"ok": False, "error": "Elige o escribe la carpeta de tu proyecto."}
    carpeta = Path(ruta.strip().strip('"')).expanduser()
    if not carpeta.is_dir():
        return {"ok": False, "error": f"La carpeta no existe: {carpeta}"}
    carpeta = carpeta.resolve()
    cfg = cfgmod.detectar(carpeta)
    existentes = []
    for docs in ("docs", *[f"{s}/docs" for r in SUGERENCIAS for s in SUGERENCIAS[r]]):
        f = flujo.ficha_destino(carpeta, docs)
        if f["instalado"]:
            existentes.append({"docs": docs, "version": f["version"], "pack": f["pack"]})
    pendiente = not existentes or any(colaboracion_pendiente(carpeta, x["docs"]) for x in existentes)
    return {"ok": True, "ruta": str(carpeta), "nombre": carpeta.name, "git": es_git(carpeta), "git_disponible": git_disponible(),
            "pila": cfg["pila"], "rol_sugerido": cfg["rol"], "instalados": existentes, "colaboracion_pendiente": pendiente,
            "sub_servidor": next((s for s in SUGERENCIAS["servidor"] if (carpeta / s).is_dir()), ""),
            "sub_cliente": next((s for s in SUGERENCIAS["cliente"] if (carpeta / s).is_dir()), "")}


def colaboracion_pendiente(repo: Path, docs: str) -> bool:
    """¿Este pack todavía no respondió a «¿Te gustaría colaborar…?»? (un pack sin instalar siempre la tiene pendiente)."""
    r, d = cfgmod.normalizar(repo, docs)
    if not flujo.ficha_destino(r, d)["instalado"]:
        return True
    return feedback.necesita_respuesta(cfgmod.cargar(r, d)[0])


def info_colaboracion() -> dict:
    """Pregunta, qué sale y qué no, para la pantalla (fuente única: scripts/feedback/cliente.py)."""
    return feedback.info_colaboracion()


def respuesta_colaborar(s: dict) -> bool | None:
    """True/False si la persona respondió; None si no hubo respuesta (con --si cuenta como No; en CI o con un agente queda pendiente)."""
    v = str(s.get("colaborar") or "").strip().lower()
    return True if v in ("si", "sí", "s", "yes", "y") else False if v in ("no", "n") else None


def aplicar_colaboracion(repo: Path, docs: str, s: dict, origen: str) -> list[tuple[str, str]]:
    """Registra la respuesta (solo si estaba pendiente) y envía lo nuevo si el envío está activo. Devuelve (texto, estado)."""
    pasos: list[tuple[str, str]] = []
    if colaboracion_pendiente(repo, docs) and respuesta_colaborar(s) is None and feedback.sin_persona():
        # R-25: sin una respuesta explícita, ni el CI ni un agente contestan por la persona; se le preguntará la próxima vez.
        pasos.append(("Colaborar en la mejora: pendiente. La responde una persona en el próximo «instalar» o «actualizar» "
                      "(o con «feedback.py activar|revocar»)", "aviso"))
    elif colaboracion_pendiente(repo, docs):
        acepta = bool(respuesta_colaborar(s))
        try:
            feedback.registrar_respuesta(repo, docs, acepta, origen)
            pasos.append(("Colaborar en la mejora: Sí. Envío de fichas EVO activado (puedes apagarlo con «feedback.py revocar»)" if acepta
                          else "Colaborar en la mejora: No. No se enviará nada y no se volverá a preguntar", "ok"))
        except Exception as exc:  # noqa: BLE001 - la respuesta no debe romper la instalación
            pasos.append((f"No se pudo guardar tu respuesta a «colaborar»: {exc}", "aviso"))
    linea = feedback.enviar_si_corresponde(repo, docs)
    if linea:
        pasos.append((linea, "aviso" if "no se pudieron" in linea else "ok"))
    return pasos


def _sub_valida(sub: str) -> str | None:
    s = sub.strip().strip("/").replace("\\", "/")
    if s in ("", "."):
        return ""
    if ".." in s.split("/") or Path(s).is_absolute() or ":" in s:
        return None
    return s


def destinos(s: dict) -> tuple[list[dict], list[str]]:
    """Traduce la solicitud a destinos concretos (repo, rol, carpeta docs)."""
    errores: list[str] = []
    base = Path((s.get("proyecto") or "").strip().strip('"')).expanduser()
    if not base.is_dir():
        return [], ["La carpeta del proyecto no existe."]
    base = base.resolve()
    pack = s.get("pack") or "servidor"
    if pack not in ("servidor", "cliente", "ambos"):
        return [], ["Elige qué pack instalar."]
    lista: list[tuple[Path, str, str | None]] = []
    if pack == "ambos":
        if s.get("mismo_repo", True):
            ss, sc = _sub_valida(s.get("sub_servidor", "")), _sub_valida(s.get("sub_cliente", ""))
            if ss is None or sc is None:
                errores.append("Las subcarpetas deben ser rutas relativas dentro del proyecto (por ejemplo apps/api).")
            elif ss == sc:
                errores.append("Servidor y cliente necesitan carpetas distintas dentro del repositorio (por ejemplo apps/api y apps/web).")
            else:
                lista = [(base, "servidor", ss), (base, "cliente", sc)]
        else:
            otro = Path((s.get("proyecto2") or "").strip().strip('"')).expanduser()
            if not otro.is_dir():
                errores.append("La carpeta del segundo repositorio (cliente) no existe.")
            elif otro.resolve() == base:
                errores.append("Los dos repositorios deben ser carpetas distintas.")
            else:
                lista = [(base, "servidor", ""), (otro.resolve(), "cliente", "")]
    else:
        sub = _sub_valida(s.get("sub", ""))
        if sub is None:
            errores.append("La subcarpeta debe ser una ruta relativa dentro del proyecto (por ejemplo apps/api).")
        else:
            lista = [(base, pack, sub)]
    salida = []
    for r, rol, sub in lista:
        raiz, docs = cfgmod.normalizar(r, f"{sub}/docs" if sub else "docs")   # si eligió una subcarpeta de un repo git, se instala como app del monorepo
        salida.append({"repo": raiz, "rol": rol, "sub": docs.rpartition("/")[0], "docs": docs, "pack": PACKS[rol],
                       "titulo": f"{rol.capitalize()} en {raiz.name}" + (f"/{docs.rpartition('/')[0]}" if "/" in docs else "")})
    return salida, errores


def planificar(s: dict) -> dict:
    """Plan en lenguaje llano de lo que pasará, sin escribir nada."""
    lista, errores = destinos(s)
    salida = []
    for d in lista:
        repo, docs = d["repo"], d["docs"]
        f = flujo.ficha_destino(repo, docs)
        lineas: list[str] = []
        if not es_git(repo):
            lineas.append(f"Se inicializará git en «{repo.name}» (git init): uxyngraphar lo necesita para proteger el núcleo.")
        try:
            if f["instalado"]:
                modo, p = "actualizar", flujo.plan_actualizacion(d["pack"], repo, docs)
                if p["al_dia"]:
                    lineas.append(f"Ya está instalado y al día (versión {p['nueva']}). No hay nada que hacer.")
                else:
                    lineas.append(f"Ya tiene uxyngraphar {p['actual']}: se actualizará el núcleo a {p['nueva']}.")
                    lineas.append(f"{p['nuevos']} archivos nuevos y {p['reemplazar']} reemplazados. Tu contenido (fichas, instrucciones, rutas) no se toca.")
                    if p["conflictos"]:
                        lineas.append(f"{len(p['conflictos'])} archivos que editaste también cambiaron: quedarán como copia «.uxyngraphar-nuevo» para que decidas.")
                    if p["mayor"]:
                        lineas.append("Es un salto de versión mayor: requiere una instrucción aprobada; se hará desde la línea de comandos (guía actualizar-nucleo).")
            else:
                modo = "adoptar" if f["docs_existe"] else "instalar"
                p = flujo.plan_instalacion(d["pack"], repo, docs, adoptar=f["docs_existe"])
                if f["docs_existe"]:
                    lineas.append(f"Ya existe «{docs}/» con contenido: se añadirá lo que falta sin pisar nada tuyo.")
                lineas.append(f"Se copiarán {p['nuevos']} archivos del pack {p['version']} a «{docs}/» (reglas, plantillas y herramientas).")
                lineas.append(f"«{'/'.join(x for x in (d['sub'], 'AGENTES.md') if x)}» se creará junto a «docs/»: es lo único que tu agente lee al empezar.")
                if p["conflictos"]:
                    lineas.append(f"{len(p['conflictos'])} archivos ya existen y son distintos: se conservan los tuyos y el de uxyngraphar queda como «.uxyngraphar-nuevo».")
                if s.get("proteger", True):
                    lineas.append("Protección activada: los agentes no podrán editar el núcleo ni leer .env o llaves; CODEOWNERS exigirá revisión humana.")
                lineas.append("Se activará la verificación automática en cada commit (credenciales, núcleo y límite de líneas)."
                              + (" Todo bloqueante (modo estricto)." if s.get("estricto") else " Solo credenciales y núcleo bloquean; el resto avisa."))
            if colaboracion_pendiente(repo, docs):
                lineas.append({True: "Colaborar en la mejora de uxyngraphar: Sí. Se activará el envío de fichas EVO (solo cuando tú instales o actualices).",
                               False: "Colaborar en la mejora de uxyngraphar: No. No se enviará nada."}.get(respuesta_colaborar(s),
                              "Colaborar en la mejora de uxyngraphar: sin respuesta (queda pendiente en CI o con un agente)."
                              if feedback.sin_persona() else "Colaborar en la mejora de uxyngraphar: sin respuesta (cuenta como No)."))
        except Exception as exc:  # noqa: BLE001 - se muestra al usuario en lugar de romper la pantalla
            modo, lineas = "error", [f"No se puede continuar: {exc}"]
        salida.append({"titulo": d["titulo"], "modo": modo, "docs": docs, "lineas": lineas})
    return {"ok": not errores and all(x["modo"] != "error" for x in salida), "errores": errores, "destinos": salida}


def ejecutar(s: dict) -> dict:
    """Hace lo planificado. Devuelve, por destino, los pasos hechos y el diagnóstico final."""
    lista, errores = destinos(s)
    if errores:
        return {"ok": False, "errores": errores, "destinos": []}
    salida, todo_ok = [], True
    for d in lista:
        repo, docs = d["repo"], d["docs"]
        res = flujo.Resultado()
        if not es_git(repo):
            if subprocess.run(["git", "init"], cwd=repo, capture_output=True).returncode == 0:
                res.add(f"Repositorio git inicializado en «{repo.name}»")
            else:
                res.add("No se pudo ejecutar git init (¿está git instalado?)", "error")
                salida.append({"titulo": d["titulo"], "pasos": [p.__dict__ for p in res.pasos], "diagnostico": [], "ok": False})
                todo_ok = False
                continue
        f = flujo.ficha_destino(repo, docs)
        if f["instalado"]:
            if s.get("aplicar_actualizacion"):
                r = flujo.actualizar_completo(d["pack"], repo, docs)
            else:
                r = flujo.Resultado()
                r.add("Sin cambios aplicados: la actualización no fue confirmada", "aviso")
        else:
            r = flujo.instalar_completo(d["pack"], repo, docs, adoptar=f["docs_existe"], proteger=s.get("proteger", True),
                                        propietario=(s.get("propietario") or "").strip(), estricto=bool(s.get("estricto")), fuente=str(d["pack"]))
        res.pasos += r.pasos
        res.ok = res.ok and r.ok
        aplicado = not f["instalado"] or bool(s.get("aplicar_actualizacion"))
        if r.ok and not f["instalado"] and flujo.ficha_destino(repo, docs)["instalado"]:
            import api_panel   # aquí y no arriba: api_panel importa este módulo
            paso = api_panel.plantilla_al_instalar(repo, docs)   # tu plantilla de este equipo (uxyngraphar panel), si tienes
            if paso:
                res.add(*paso)
        if r.ok and aplicado and flujo.ficha_destino(repo, docs)["instalado"]:
            for texto, estado in aplicar_colaboracion(repo, docs, s, "actualizador" if f["instalado"] else "instalador"):
                res.add(texto, estado)
        diag = flujo.diagnostico(repo, docs) if r.ok and (repo / docs).is_dir() else flujo.Resultado()
        todo_ok = todo_ok and res.ok
        salida.append({"titulo": d["titulo"], "docs": docs, "repo": str(repo), "ok": res.ok, "pasos": [p.__dict__ for p in res.pasos],
                       "diagnostico": [p.__dict__ for p in diag.pasos if p.estado != "ok"], "diagnostico_ok": sum(1 for p in diag.pasos if p.estado == "ok")})
    return {"ok": todo_ok, "errores": [], "destinos": salida}


def siguientes_pasos(s: dict) -> list[str]:
    lista, _ = destinos(s)
    rutas = [d["docs"] for d in lista] or ["docs"]
    config = " y ".join(f"{r}/00-nucleo/configuracion-proyecto.md" for r in rutas)
    agentes = " y ".join(f"{r.rpartition('/')[0]}/AGENTES.md" if "/" in r else "AGENTES.md" for r in rutas)
    carpetas = ", ".join(f"{r}/" for r in rutas)
    return [f"Abre {config} y completa el nombre, el repositorio y las rutas de tu código.",
            f"Revisa {' y '.join(r + '/uxyngraphar.config.json' for r in rutas)}: es la configuración propia del proyecto (controles, idioma, commits, respaldos). Guía: {rutas[0]}/10-guias/configuracion-uxyngraphar.md",
            f"Haz commit de lo nuevo: {agentes}, {carpetas}, .claude/ y .github/CODEOWNERS.",
            "Abre tu agente (por ejemplo Claude Code) en el proyecto y pídele cualquier tarea: leerá solo AGENTES.md y te propondrá una instrucción para aprobar antes de tocar código.",
            f"En tu CI, ejecuta controlar.py --base origin/main (guía: {rutas[0]}/10-guias/control-de-construccion.md): es la barrera que no se puede saltar en local."]
