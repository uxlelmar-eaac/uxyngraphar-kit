"""Doctor de uxyngraphar: diagnóstico integral de un proyecto que usa el protocolo (solo lectura salvo `arreglar`)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "decisiones"))
sys.path.insert(0, str(AQUI.parent / "ganchos"))
sys.path.insert(0, str(AQUI.parent / "tokens"))

import ci  # noqa: E402
import clasificacion as cl  # noqa: E402
import instalar as ins  # noqa: E402
import lock  # noqa: E402
import proteccion  # noqa: E402
import transaccion  # noqa: E402
import verificar as ver  # noqa: E402

sys.path.insert(0, str(AQUI.parent / "control"))
import escaneo  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402

NIVELES = ("ERROR", "WARN", "INFO", "OK")
PLACEHOLDERS = ("<nombre>", "<org>/<repo>", "<org>/<repo-frontend>", "<repo-backend>")


@dataclass
class Chequeo:
    id: str
    nivel: str
    mensaje: str
    arreglo: str = ""


def _c(id: str, nivel: str, msg: str, arreglo: str = "") -> Chequeo:
    return Chequeo(id, nivel, msg, arreglo)


def entorno(repo: Path) -> list[Chequeo]:
    out = [_c("python", "OK" if sys.version_info >= (3, 10) else "ERROR", f"Python {sys.version_info.major}.{sys.version_info.minor}",
              "" if sys.version_info >= (3, 10) else "Instala Python 3.10 o superior")]
    out.append(_c("git", "OK", "Repositorio git") if ins.es_repo(repo) else _c("git", "ERROR", f"{repo} no es un repositorio git", "git init"))
    return out


def estado_lock(repo: Path, docs: str) -> list[Chequeo]:
    datos = lock.leer(repo, docs)
    if datos is None:
        return [_c("lock", "ERROR", "No hay .uxyngraphar.lock: el núcleo no tiene línea base", "instalar-pack.py (proyecto nuevo) o actualizar-pack.py --apply (proyecto ya instalado sin lock)")]
    out = [_c("lock", "OK", f"Lock presente · pack {datos.get('pack')} {datos.get('version')} · perfil {datos.get('perfil')}")]
    if datos.get("danado"):
        out = [_c("lock", "WARN", datos["danado"], "Actualiza (uxyngraphar actualizar o actualizar-pack.py --apply): se vuelve a escribir sano")]
    if transaccion.interrumpidas(repo):
        out.append(_c("actualizacion-interrumpida", "ERROR", "Una actualización se cortó a mitad y dejó archivos mezclados",
                      "doctor.py --fix (o vuelve a actualizar): la deshace y el proyecto queda como estaba antes"))
    if lock.es_ruta_local(datos.get("fuente", "")):
        out.append(_c("lock-fuente", "WARN", "El lock guarda una ruta local de tu equipo en «fuente» (se publicaría en el repositorio)", "doctor.py --fix"))
    if not lock.sello_valido(datos):
        out.append(_c("lock-sello", "ERROR", "El lock fue editado a mano (sello inválido)", "verificar-nucleo.py --contra RUTA_PACK y actualizar-pack.py --apply --restaurar-nucleo"))
    return out


def raiz_agentes(repo: Path, docs: str = "docs") -> list[Chequeo]:
    faltan = [cl.destino(n, docs) for n in cl.EN_RAIZ if not (repo / cl.destino(n, docs)).is_file()]
    if faltan:
        return [_c("agentes-raiz", "ERROR", f"Falta junto a docs/: {', '.join(faltan)}", "actualizar-pack.py --apply")]
    import medir
    filas = medir.arranque(repo, docs)
    total = sum(t for _, t in filas)
    return [_c("agentes-raiz", "OK", "AGENTES.md y AGENTS.md junto a docs/"),
            _c("arranque", "OK" if total <= medir.ARRANQUE_MAX else "WARN", f"Costo de arranque del agente: ~{total} tokens (límite {medir.ARRANQUE_MAX})",
               "" if total <= medir.ARRANQUE_MAX else "Acorta docs/ESTADO.md (decisiones.py estado --escribir) o mueve detalle a 00-nucleo/agentes-detalle.md")]


def integridad(repo: Path, docs: str, pack: Path | None) -> list[Chequeo]:
    hallazgos = ver.verificar(repo, docs)
    if pack:
        hallazgos += ver.contra_pack(repo, docs, pack)
        v_pack, datos = lock.version_de(pack), lock.leer(repo, docs) or {}
        if datos.get("version") and v_pack != datos["version"]:
            hallazgos_v = [_c("version", "WARN", f"Hay una versión más nueva del pack: {datos['version']} → {v_pack}", "actualizar-pack.py RUTA_PACK --apply")]
        else:
            hallazgos_v = [_c("version", "OK", f"Núcleo en la versión del pack ({v_pack})")]
    else:
        hallazgos_v = [_c("version", "INFO", "Sin --pack: no se comprueba si hay versión nueva ni se contrasta con la fuente")]
    if not hallazgos:
        return [_c("nucleo", "OK", "Núcleo íntegro")] + hallazgos_v
    out = [_c(h.codigo.lower(), "ERROR", f"{h.ruta}: {h.mensaje}", "No repares a mano: actualizar-pack.py --apply --restaurar-nucleo (humano)") for h in hallazgos[:15]]
    if len(hallazgos) > 15:
        out.append(_c("nucleo", "ERROR", f"…y {len(hallazgos) - 15} hallazgos más"))
    return out + hallazgos_v


def proteccion_activa(repo: Path, docs: str) -> list[Chequeo]:
    out: list[Chequeo] = []
    cfg = repo / ".claude" / "settings.json"
    try:
        deny = json.loads(cfg.read_text(encoding="utf-8")).get("permissions", {}).get("deny", []) if cfg.is_file() else []
    except ValueError:
        deny = []
    esperadas = {f"{h}({r})" for r in proteccion.rutas_protegidas(repo, docs) for h in ("Edit", "Write")}
    faltan = esperadas - set(deny)
    out.append(_c("deny", "OK", "Reglas deny para agentes completas") if not faltan else
               _c("deny", "WARN", f"Faltan {len(faltan)} reglas deny en .claude/settings.json (los agentes podrían editar el núcleo)", "doctor.py --fix"))
    co = repo / ".github" / "CODEOWNERS"
    texto = co.read_text(encoding="utf-8") if co.is_file() else ""
    if proteccion.MARCA_INI not in texto:
        out.append(_c("codeowners", "WARN", "CODEOWNERS no protege el núcleo", "instalar-pack.py --proteger --propietario @usuario (o añadir el bloque a mano)"))
    elif "@CAMBIAR-PROPIETARIO" in texto:
        out.append(_c("codeowners", "WARN", "CODEOWNERS conserva el propietario de ejemplo", "Sustituye @CAMBIAR-PROPIETARIO por el usuario/equipo real"))
    else:
        out.append(_c("codeowners", "OK", "CODEOWNERS protege el núcleo"))
    import instalar_ganchos
    try:
        gancho = instalar_ganchos.dir_ganchos(repo) / "pre-commit"   # respeta core.hooksPath, worktrees y subcarpetas del repo
    except (RuntimeError, OSError):
        gancho = repo / ".git" / "hooks" / "pre-commit"
    vigilados = instalar_ganchos.docs_del_gancho(gancho)
    if not instalar_ganchos.es_nuestro(gancho):
        out.append(_c("gancho", "WARN", "No hay gancho pre-commit de uxyngraphar: los commits no se verifican automáticamente", "python3 " + docs + "/scripts/instalar-ganchos.py --docs " + docs + "  (o doctor.py --fix)"))
    elif vigilados and docs not in vigilados:
        out.append(_c("gancho", "WARN", f"El gancho pre-commit existe pero no vigila este pack ({docs})", "python3 " + docs + "/scripts/instalar-ganchos.py --docs " + docs))
    else:
        out.append(_c("gancho", "OK", "Gancho pre-commit instalado"))
    return out


def gitignore(repo: Path, docs: str) -> list[Chequeo]:
    faltan = ins.asegurar_gitignore(repo, docs, True)
    return [_c("gitignore", "OK", ".gitignore al día")] if not faltan else [_c("gitignore", "WARN", f"Faltan en .gitignore: {', '.join(faltan)}", "doctor.py --fix")]


def servidor(repo: Path, docs: str) -> list[Chequeo]:
    """CI que ejecute uxyngraphar, workflows mal ubicados, bytecode versionado y finales de línea del pack."""
    out = [_c(*t) for t in ci.chequeos(repo, docs)]
    pyc = [p for p in ci.git_lineas(repo, "ls-files", "--", "*.pyc")]
    out.append(_c("pyc", "WARN", f"{len(pyc)} archivo(s) .pyc versionados (p. ej. {pyc[0]})", "git rm -r --cached <carpeta __pycache__> y doctor.py --fix (añade __pycache__/ y *.pyc a .gitignore)") if pyc else _c("pyc", "OK", "Sin bytecode versionado"))
    faltan = ins.asegurar_gitattributes(repo, docs, True)
    out.append(_c("gitattributes", "OK", ".gitattributes fija LF para el pack") if not faltan else
               _c("gitattributes", "WARN", "Sin .gitattributes del pack: en Windows el hash del núcleo y los scripts pueden romperse por CRLF", "doctor.py --fix"))
    return out


def estructura(repo: Path, docs: str) -> list[Chequeo]:
    val = repo / docs / "scripts" / "validar-documentacion.py"
    if not val.is_file():
        return [_c("validador", "ERROR", "Falta scripts/validar-documentacion.py", "actualizar-pack.py --apply")]
    r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(val), str(repo / docs)], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=repo)
    lineas = (r.stdout + r.stderr).splitlines()
    errores, avisos = [l for l in lineas if l.startswith("ERROR")], [l for l in lineas if l.startswith("WARN")]
    if errores:
        return [_c("validador", "ERROR", f"{len(errores)} error(es) de validación; primero: {errores[0][:140]}", "validar-documentacion.py para el detalle")]
    return [_c("validador", "WARN" if avisos else "OK", f"Validador sin errores" + (f", {len(avisos)} aviso(s)" if avisos else ""), "validar-documentacion.py para el detalle" if avisos else "")]


def configuracion(repo: Path, docs: str) -> list[Chequeo]:
    f = repo / docs / "00-nucleo" / "configuracion-proyecto.md"
    if not f.is_file():
        return [_c("config", "ERROR", "Falta 00-nucleo/configuracion-proyecto.md")]
    pend = [p for p in PLACEHOLDERS if p in f.read_text(encoding="utf-8")]
    return [_c("config", "OK", "configuracion-proyecto.md rellena")] if not pend else [_c("config", "WARN", f"configuracion-proyecto.md con placeholders sin rellenar: {', '.join(pend)}", "Rellena nombre, repositorio y rutas de código")]


def control(repo: Path, docs: str) -> list[Chequeo]:
    if not (repo / docs / cfgmod.NOMBRE).is_file():
        return [_c("control", "INFO", f"Sin {cfgmod.NOMBRE}: la puerta de control usa valores por defecto", "instalar-pack.py lo genera; o créalo (10-guias/control-de-construccion.md)")]
    cfg, problemas = cfgmod.cargar(repo, docs)
    if problemas:
        return [_c("control", "ERROR", f"{cfgmod.NOMBRE}: {problemas[0]}", "Corrige el archivo (niveles: bloqueante|aviso|apagado)")]
    if not cfg["codigo"]["extensiones"]:
        return [_c("control", "WARN", "Config sin pila detectada (codigo.extensiones vacío): la puerta mide casi nada", f"Rellena codigo.raices y codigo.extensiones en {docs}/{cfgmod.NOMBRE}")]
    apagados = [k for k, v in cfg["niveles"].items() if v == "apagado"]
    return [_c("control", "WARN" if apagados else "OK", f"Puerta de control activa ({', '.join(cfg['pila']) or 'pila manual'}; límite {cfg['limite_lineas']} líneas)" + (f"; apagados: {', '.join(apagados)}" if apagados else ""), "Reactiva los controles apagados o documenta por qué" if apagados else "")]


def secretos(repo: Path, docs: str) -> list[Chequeo]:
    if not (repo / ".git").exists():
        return []
    cfg, _ = cfgmod.cargar(repo, docs)
    hallazgos = escaneo.arbol(repo, cfg.get("secretos_permitir", []))
    f = repo / ".claude" / "settings.json"
    sin_deny = "Read(.env)" not in (f.read_text(encoding="utf-8") if f.is_file() else "")
    if hallazgos:
        h = hallazgos[0]
        return [_c("secretos", "ERROR", f"{len(hallazgos)} posible(s) credencial(es) en el árbol; primera: {h.ruta}:{h.linea} ({h.tipo})", "Ejecuta escanear-secretos.py para ver archivo y línea. Si es un valor de prueba falso: añade «uxyngraphar:permitir-secreto» en esa línea o la ruta en secretos_permitir de uxyngraphar.config.json. Si es real: rótala y usa variables de entorno")]
    if sin_deny:
        return [_c("secretos", "WARN", "Sin credenciales en el árbol, pero los agentes pueden leer .env/llaves (faltan reglas deny)", "instalar-pack.py --proteger (o doctor.py --fix)")]
    return [_c("secretos", "OK", "Sin credenciales en el árbol; agentes sin acceso a .env/llaves")]


def residuos(repo: Path, docs: str, hoy: date) -> list[Chequeo]:
    out: list[Chequeo] = []
    nuevos = [p.relative_to(repo).as_posix() for p in (repo / docs).rglob("*.uxyngraphar-nuevo")] + [p.relative_to(repo).as_posix() for p in repo.glob("*.uxyngraphar-nuevo")]
    out.append(_c("conflictos", "OK", "Sin conflictos de actualización pendientes") if not nuevos else
               _c("conflictos", "WARN", f"{len(nuevos)} conflicto(s) de actualización sin resolver: {', '.join(nuevos[:3])}", "Compara cada .uxyngraphar-nuevo con su original, resuelve y bórralo"))
    try:
        import respaldos
        todos, viejos, pol = respaldos.listar(repo, docs), respaldos.caducados(repo, docs), respaldos.politica(repo, docs)
    except Exception as exc:  # noqa: BLE001 - un respaldo ilegible no debe tumbar el diagnóstico
        out.append(_c("respaldos", "WARN", f"No pude revisar las copias de seguridad: {exc}", "Revisa .uxyngraphar-respaldo/ y docs/.depuracion/respaldo/"))
        return out
    if viejos:
        auto = "se borrarán solas en la próxima actualización o depuración" if pol.get("limpieza_automatica", True) else "la limpieza automática está desactivada"
        out.append(_c("respaldos", "INFO", f"{len(viejos)} de {len(todos)} copia(s) de seguridad superan {pol['conservar_dias']} días ({auto})",
                      f"Para borrarlas ya: python3 {docs}/scripts/respaldos.py limpiar --docs {docs} --aplicar · guía: {docs}/10-guias/respaldos.md"))
    return out


def colas(repo: Path, docs: str, hoy: date) -> list[Chequeo]:
    try:
        from depurar import diagnosticar
        from metricas import fichas
    except ImportError:
        return [_c("colas", "WARN", "No se pudo cargar el tooling de decisiones", "actualizar-pack.py --apply")]
    raiz = repo / docs
    viejas = [f for f in fichas(raiz) if f["estado"] == "01-pendientes" and (hoy - date.fromisoformat(f["fecha"])).days > 30]
    out = [_c("pendientes", "OK", "Sin pendientes con más de 30 días") if not viejas else
           _c("pendientes", "WARN", f"{len(viejas)} pendiente(s) con más de 30 días (p. ej. {viejas[0]['id']})", "decisiones.py scan  → revisar y decidir")]
    d = diagnosticar(raiz, hoy)
    if d["mover"] or d["vencidas"]:
        out.append(_c("depuracion", "INFO", f"Depuración sugerida: {len(d['mover'])} por mover, {len(d['vencidas'])} listas para eliminar vencidas", "decisiones.py depurar --plan plan.json"))
    if d["anclas_huerfanas"] or d["espejo_huerfano"]:
        out.append(_c("huerfanos", "INFO", f"{len(d['anclas_huerfanas'])} ancla(s) de código y {len(d['espejo_huerfano'])} archivo(s) de espejo huérfanos", "decisiones.py depurar"))
    return out


def memoria(repo: Path, docs: str) -> list[Chequeo]:
    """R-24: la memoria existe y nadie la alteró a mano (catálogo y huellas)."""
    if not (repo / docs / "95-memoria").is_dir():
        return [_c("memoria", "WARN", "Falta la memoria del sistema (95-memoria/)", "Actualiza el pack: actualizar-pack.py --apply (o uxyngraphar actualizar)")]
    sys.path.insert(0, str(AQUI.parent / "memoria"))
    import almacen
    problemas = almacen.verificar(repo / docs)
    if problemas:
        return [_c("memoria", "ERROR", f"Memoria alterada fuera de memoria.py: {problemas[0]}" + (f" (y {len(problemas) - 1} más)" if len(problemas) > 1 else ""),
                   "Restaura desde git (git checkout -- docs/95-memoria) y usa memoria.py para cualquier cambio")]
    return [_c("memoria", "OK", f"Memoria del sistema íntegra · {len(almacen.vigentes(repo / docs))} memoria(s)")]


def ajustes(repo: Path, docs: str) -> list[Chequeo]:
    """R-25: los ajustes locales siguen cuadrando con el núcleo instalado."""
    sys.path.insert(0, str(AQUI.parent / "ajustes"))
    import ajustes_locales as aj
    revisados = aj.revisar(repo / docs)
    activos = [a for a in revisados if a.status == "activo"]
    pendientes = [a for a in revisados if a.problemas]
    if pendientes:
        return [_c("ajustes", "WARN", f"{len(pendientes)} ajuste(s) local(es) por revisar; primero: {pendientes[0].id} ({pendientes[0].problemas[0]})",
                   f"python3 {docs}/scripts/ajustes.py verificar · luego «revisado ID» o «retirar ID»")]
    if not activos:
        return []
    return [_c("ajustes", "OK", f"{len(activos)} ajuste(s) local(es) activo(s) y al día con el núcleo")]


def reglas_proyecto(repo: Path, docs: str) -> list[Chequeo]:
    """Reglas del proyecto (96-reglas-proyecto/): frontmatter válido e INDICE.md al día con las reglas activas."""
    if not (repo / docs / "96-reglas-proyecto").is_dir():
        return []
    sys.path.insert(0, str(AQUI.parent / "reglas"))
    import reglas_proyecto as rp
    todas = rp.todas(repo / docs)
    malas = [r for r in todas if r.problemas]
    if malas:
        return [_c("reglas_proyecto", "ERROR", f"{len(malas)} regla(s) del proyecto inválida(s); primera: {malas[0].ruta.name} ({malas[0].problemas[0]})",
                   "Corrige el frontmatter según 96-reglas-proyecto/_PLANTILLA-regla.md (con una instrucción aprobada)")]
    if not rp.indice_al_dia(repo / docs):
        return [_c("reglas_proyecto", "ERROR", "96-reglas-proyecto/INDICE.md no cuadra con las reglas activas",
                   f"python3 {docs}/scripts/reglas.py indice")]
    return [_c("reglas_proyecto", "OK", f"Reglas del proyecto: {sum(1 for r in todas if r.activa)} activa(s), índice al día")]


def diagnosticar(repo: Path, docs: str = "docs", pack: Path | None = None, hoy: date | None = None) -> list[Chequeo]:
    docs, hoy = docs.strip("/"), hoy or date.today()
    resultado = entorno(repo)
    if not (repo / docs).is_dir():
        return resultado + [_c("docs", "ERROR", f"No existe {docs}/ en {repo}", "instalar-pack.py")]
    for paso in (lambda: estado_lock(repo, docs), lambda: raiz_agentes(repo, docs), lambda: integridad(repo, docs, pack), lambda: proteccion_activa(repo, docs),
                 lambda: gitignore(repo, docs), lambda: servidor(repo, docs), lambda: estructura(repo, docs), lambda: configuracion(repo, docs), lambda: control(repo, docs), lambda: secretos(repo, docs), lambda: memoria(repo, docs), lambda: ajustes(repo, docs), lambda: reglas_proyecto(repo, docs), lambda: residuos(repo, docs, hoy),
                 lambda: colas(repo, docs, hoy)):
        resultado += paso()
    return resultado


def arreglar(repo: Path, docs: str) -> list[str]:
    """Correcciones seguras e idempotentes: .gitignore, reglas deny y gancho pre-commit. Nunca toca el núcleo ni el contenido."""
    import instalar_ganchos
    hechas = transaccion.recuperar(repo)
    if ins.asegurar_gitignore(repo, docs, False):
        hechas.append(".gitignore actualizado")
    if ins.asegurar_gitattributes(repo, docs, False):
        hechas.append(".gitattributes actualizado")
    datos = lock.leer(repo, docs)
    if datos and lock.es_ruta_local(datos.get("fuente", "")):
        datos["fuente"] = lock.etiqueta_fuente(datos["fuente"], datos.get("version", ""))
        lock.escribir(repo, docs, datos)
        hechas.append("lock: «fuente» ya no guarda una ruta local")
    if lock.leer(repo, docs):
        proteccion.reglas_agente(repo, docs)
        hechas.append("reglas deny regeneradas")
        hechas += [f"{n}: memoria y respaldos fuera del alcance de la IA" for n in proteccion.exclusiones_agentes(repo, docs)]
        dueno = proteccion.propietario_actual(repo, docs)
        if dueno:   # el bloque de CODEOWNERS existe: se regenera para incluir lo nuevo que protege el pack
            proteccion.codeowners(repo, docs, dueno)
            hechas.append("CODEOWNERS regenerado" + (" (sigue con el propietario de ejemplo)" if "CAMBIAR" in dueno else ""))
    if not ci._ejecuta_uxyngraphar(repo):
        hechas.append(f"CI creado: {ci.workflow(repo, docs)[0].relative_to(repo).as_posix()}")
    try:
        instalar_ganchos.instalar(repo, docs)
        hechas.append("gancho pre-commit instalado")
    except FileExistsError as exc:
        hechas.append(f"gancho NO instalado: {exc}")
    return hechas


def formatear(chequeos: list[Chequeo]) -> str:
    marca = {"ERROR": "✗", "WARN": "!", "INFO": "i", "OK": "✓"}
    l = ["uxyngraphar doctor: revisa que el protocolo esté instalado y sano en este proyecto.",
         "Solo lee; no cambia nada (con --fix aplica correcciones seguras). Lo urgente aparece primero.\n"]
    for c in sorted(chequeos, key=lambda c: NIVELES.index(c.nivel)):
        l.append(f" {marca[c.nivel]} [{c.nivel}] {c.mensaje}")
        if c.arreglo and c.nivel != "OK":
            l.append(f"      → {c.arreglo}")
    cuenta = {n: sum(1 for c in chequeos if c.nivel == n) for n in NIVELES}
    l.append(f"\nResumen: {cuenta['ERROR']} error(es) · {cuenta['WARN']} aviso(s) · {cuenta['INFO']} info · {cuenta['OK']} ok")
    if cuenta["ERROR"]:
        l.append("Qué hacer ahora: corrige primero los ✗ (cada uno trae su «→» con el arreglo). Luego vuelve a ejecutar el doctor.")
    elif cuenta["WARN"]:
        l.append("Qué hacer ahora: nada es urgente; revisa los «!» cuando puedas (cada uno trae su «→» con el arreglo).")
    else:
        l.append("Todo en orden. Nada que hacer.")
    return "\n".join(l)


def a_json(chequeos: list[Chequeo]) -> str:
    return json.dumps([asdict(c) for c in chequeos], ensure_ascii=False, indent=2)
