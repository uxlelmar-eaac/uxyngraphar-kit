"""Importar sin perder nada: un zip, varios archivos o una carpeta se adaptan al esqueleto completo de un sistema.

Primero se crea el esqueleto de serie (`catalogo.crear`: núcleo, prompts/, config/ y las piezas con contenido de
arranque) y después se colocan encima los archivos de la persona:

  - los reconocibles van a su sitio (README.md, LIMITES.md… en la raíz; `docs/` → `referencia/`, `templates/` →
    `plantillas/`, prompts sueltos → `prompts/`, configuraciones sueltas → `config/`…) y sustituyen al de la base;
  - `sistema.json` y los JSON de `config/` que chocan con los de la base se fusionan: los valores de la persona mandan;
  - todo lo demás se conserva en su ruta relativa original (con el nombre saneado a ASCII sin espacios si hace falta),
    incluidos los binarios;
  - lo que la construcción añade sola (`INTEGRIDAD.json`, `scripts/comun/`) se guarda en `importado/` en vez de tirarlo.

Solo se ignora basura de sistema (`__MACOSX/`, `.DS_Store`, `__pycache__/`, `*.pyc`, `.git/`), y se dice cuál.
Devuelve el resumen: qué se mapeó, qué puso la base, qué se conservó tal cual, qué se fusionó y qué se renombró.
"""
from __future__ import annotations

import base64
import io
import json
import re
import shutil
import stat
import tempfile
import unicodedata
import zipfile
from pathlib import Path

import catalogo
import entrada
import especificacion as esp
import nomenclatura

base = esp.base

MAX_ARCHIVOS = 400
MAX_BYTES_TOTAL = 20 * 1024 * 1024
OCULTA = ".importando-"
BASURA = re.compile(r"(?:^|/)(?:__MACOSX|\.git|__pycache__|node_modules)(?:/|$)|(?:^|/)(?:\.DS_Store|Thumbs\.db|desktop\.ini)$|\.pyc$")
NUCLEO_RAIZ = {n.lower(): n for n in (*base.NUCLEO, "CHANGELOG.md", "HERRAMIENTAS.md", "COMPONENTES.md")}
CARPETAS = {
    "proceso": "proceso", "fases": "proceso", "flujos": "proceso", "flows": "proceso", "workflows": "proceso",
    "skills": "skills", "skill": "skills",
    "plantillas": "plantillas", "plantilla": "plantillas", "templates": "plantillas", "template": "plantillas",
    "referencia": "referencia", "referencias": "referencia", "docs": "referencia", "doc": "referencia",
    "documentacion": "referencia", "recursos": "referencia", "resources": "referencia", "reference": "referencia",
    "ejemplos": "ejemplos", "ejemplo": "ejemplos", "examples": "ejemplos", "example": "ejemplos",
    "pruebas": "pruebas", "tests": "pruebas", "test": "pruebas",
    "andamiaje": "andamiaje",
    "prompts": "prompts", "prompt": "prompts",
    "config": "config", "configs": "config", "configuracion": "config", "settings": "config", "ajustes": "config",
}
CONFIG = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env"}
DOCUMENTOS = {".md", ".txt", ".pdf", ".rst", ".doc", ".docx", ".odt", ".html"}


class ImportacionInvalida(ValueError):
    pass


# ── entradas ────────────────────────────────────────────────────────────────

def _seguro(nombre: str) -> bool:
    partes = nombre.replace("\\", "/").strip("/").split("/")
    return bool(nombre) and not nombre.startswith(("/", "\\")) and ":" not in partes[0] and not any(p in ("", ".", "..") for p in partes)


def desde_zip(datos: bytes) -> dict[str, bytes]:
    try:
        z = zipfile.ZipFile(io.BytesIO(datos))
    except zipfile.BadZipFile:
        raise ImportacionInvalida("el archivo no es un zip válido") from None
    salida: dict[str, bytes] = {}
    total = 0
    with z:
        for e in z.infolist():
            if e.is_dir():
                continue
            if not _seguro(e.filename):
                raise ImportacionInvalida(f"ruta no aceptada en el zip: {e.filename!r}")
            if stat.S_ISLNK(e.external_attr >> 16):
                raise ImportacionInvalida(f"enlace simbólico no aceptado: {e.filename!r}")
            if e.flag_bits & 0x1:
                raise ImportacionInvalida(f"archivo cifrado: {e.filename!r}")
            total += e.file_size
            if total > MAX_BYTES_TOTAL:
                raise ImportacionInvalida(f"demasiado grande al descomprimir (máximo {MAX_BYTES_TOTAL // (1024 * 1024)} MB)")
            salida[e.filename.replace("\\", "/")] = z.read(e)
    return salida


def desde_carpeta(ruta: Path) -> dict[str, bytes]:
    ruta = Path(ruta).expanduser().resolve()
    if not ruta.is_dir():
        raise ImportacionInvalida(f"no existe la carpeta {ruta}")
    salida, total = {}, 0
    for p in sorted(ruta.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(ruta).as_posix()
        if BASURA.search(rel):
            continue
        total += p.stat().st_size
        if total > MAX_BYTES_TOTAL:
            raise ImportacionInvalida(f"la carpeta es demasiado grande (máximo {MAX_BYTES_TOTAL // (1024 * 1024)} MB)")
        salida[ruta.name + "/" + rel] = p.read_bytes()
    return salida


def desde_lista(archivos: list[dict]) -> dict[str, bytes]:
    """[{ruta, datos (base64)} | {ruta, contenido (texto)}] → {ruta: bytes} (lo que manda el panel)."""
    salida = {}
    for a in archivos or []:
        ruta = str(a.get("ruta") or a.get("nombre") or "").replace("\\", "/")
        if not _seguro(ruta):
            raise ImportacionInvalida(f"ruta no aceptada: {ruta!r}")
        if "datos" in a:
            try:
                salida[ruta] = base64.b64decode(str(a["datos"]), validate=True)
            except ValueError:
                raise ImportacionInvalida(f"{ruta}: datos base64 no válidos") from None
        else:
            salida[ruta] = str(a.get("contenido") or "").encode("utf-8")
    if sum(len(v) for v in salida.values()) > MAX_BYTES_TOTAL:
        raise ImportacionInvalida(f"demasiado grande (máximo {MAX_BYTES_TOTAL // (1024 * 1024)} MB)")
    return salida


# ── normalización y mapeo ───────────────────────────────────────────────────

def _ascii(parte: str) -> str:
    t = unicodedata.normalize("NFKD", parte).encode("ascii", "ignore").decode()
    t = re.sub(r"\s+", "-", t.strip())
    t = re.sub(r"[^A-Za-z0-9._+-]", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t or "archivo"


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z]+", "-", t).strip("-")
    return t


def _quitar_raiz_comun(rutas: dict[str, bytes]) -> tuple[dict[str, bytes], str]:
    primeras = {r.split("/")[0] for r in rutas}
    if len(primeras) == 1 and all("/" in r for r in rutas):
        (raiz,) = primeras
        if raiz.lower() in CARPETAS:   # «prompts/uno.md» suelto: es una carpeta del sistema, no un envoltorio
            return rutas, ""
        return {r.split("/", 1)[1]: v for r, v in rutas.items()}, raiz
    return rutas, ""


def destino_de(rel: str) -> tuple[str, str]:
    """(ruta en el sistema, motivo) para un archivo importado con ruta ya saneada `rel`."""
    partes = rel.split("/")
    nombre = partes[-1]
    if rel == base.INTEGRIDAD or rel.startswith("scripts/comun/"):
        return f"importado/{rel}", "lo genera la construcción: se guarda aparte para no perderlo"
    if len(partes) == 1:
        if nombre.lower() in NUCLEO_RAIZ:
            return NUCLEO_RAIZ[nombre.lower()], "archivo del núcleo"
        sufijo = Path(nombre).suffix.lower()
        if "prompt" in nombre.lower() or sufijo == ".prompt":
            return f"prompts/{nombre}", "prompt"
        if sufijo in CONFIG:
            return f"config/{nombre}", "configuración"
        if sufijo in DOCUMENTOS:
            return f"referencia/{nombre}", "documento de consulta"
        return rel, ""
    canon = CARPETAS.get(partes[0].lower())
    if canon:
        nuevo = "/".join([canon, *partes[1:]])
        return nuevo, ("" if nuevo == rel else f"«{partes[0]}/» es «{canon}/» en un sistema de gobernanza")
    return rel, ""


def _fusionar(base_d, usuario):
    """Fusión profunda: los dicts se combinan, en todo lo demás manda el valor de la persona."""
    if isinstance(base_d, dict) and isinstance(usuario, dict):
        salida = dict(base_d)
        for k, v in usuario.items():
            salida[k] = _fusionar(base_d.get(k), v) if k in base_d else v
        return salida
    return usuario


def fusionar_manifiesto(m_base: dict, m_usuario: dict, pid: str, titulo: str) -> tuple[dict, list[str]]:
    """Manifiesto de la base + el de la persona (manda la persona) con id, título y formato del sistema creado."""
    avisos = []
    fijos = {"manifiesto_formato": m_base["manifiesto_formato"], "id": pid, "titulo": titulo}
    for k in ("id", "titulo"):
        if k in m_usuario and m_usuario[k] != fijos[k]:
            avisos.append(f"sistema.json: «{k}» era «{m_usuario[k]}»; queda «{fijos[k]}» (el del sistema creado)")
    m = _fusionar(m_base, {k: v for k, v in m_usuario.items() if k not in fijos and k != "piezas"})
    if not base.SEMVER.match(str(m.get("version", ""))):
        m["version"] = m_base["version"]
    m.update(fijos)
    m["activacion"] = list(dict.fromkeys([*(m_base.get("activacion") or []), *(m_usuario.get("activacion") or [])]))
    m["piezas"] = sorted(set(m_base.get("piezas") or []) | {p for p in (m_usuario.get("piezas") or []) if p in base.PIEZAS},
                         key=list(base.PIEZAS).index)
    return {"manifiesto_formato": m.pop("manifiesto_formato"), "id": m.pop("id"), **m}, avisos


# ── importación ─────────────────────────────────────────────────────────────

def _manifiesto_de(archivos: dict[str, bytes]) -> dict:
    datos = archivos.get(base.MANIFIESTO)
    if datos is None:
        return {}
    try:
        m = json.loads(datos.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {}
    return m if isinstance(m, dict) else {}


def _titulo_de(pid: str) -> str:
    t = pid.replace("-", " ")
    return t[:1].upper() + t[1:]


def importar(archivos: dict[str, bytes], pid: str = "", titulo: str = "", descripcion: str = "", familia: str = "",
             raiz: Path | None = None, aplicar: bool = True, nombre_origen: str = "") -> dict:
    """Crea un sistema con el esqueleto completo y coloca encima `archivos` ({ruta: bytes}) sin descartar ninguno.

    Con `aplicar=False` no toca el catálogo: devuelve el mismo resumen como vista previa."""
    if not archivos:
        raise ImportacionInvalida("no hay archivos que importar")
    ignorados = sorted(r for r in archivos if BASURA.search(r))
    archivos = {r: v for r, v in archivos.items() if not BASURA.search(r)}
    if not archivos:
        raise ImportacionInvalida("solo había archivos de sistema (.DS_Store, __MACOSX…): nada que importar")
    if len(archivos) > MAX_ARCHIVOS:
        raise ImportacionInvalida(f"demasiados archivos ({len(archivos)}; máximo {MAX_ARCHIVOS})")
    archivos, raiz_comun = _quitar_raiz_comun(archivos)
    renombrados = []
    limpios: dict[str, bytes] = {}
    for r, v in sorted(archivos.items()):
        nuevo = "/".join(_ascii(p) for p in r.split("/"))
        if nuevo != r:
            renombrados.append({"de": r, "a": nuevo})
        while nuevo in limpios:
            nuevo = _con_sufijo(nuevo)
        limpios[nuevo] = v
    m_usuario = _manifiesto_de(limpios)
    pid = (pid or str(m_usuario.get("id") or "") or slug(str(m_usuario.get("titulo") or ""))
           or slug(Path(nombre_origen).stem if nombre_origen else "") or slug(raiz_comun)).strip()
    if not pid:
        raise ImportacionInvalida("indica el identificador del sistema")
    if not titulo:
        candidato = str(m_usuario.get("titulo") or "")
        titulo = candidato if candidato and not nomenclatura.problemas_titulo(pid, candidato) else _titulo_de(pid)
    if not familia:
        propia = str(m_usuario.get("familia") or "")
        familia = propia if propia in nomenclatura.NORMA["familias"] else "proceso"
    descripcion = descripcion or str(m_usuario.get("descripcion") or "") or titulo

    destino = catalogo.catalogo(raiz) / pid
    if destino.exists():
        raise FileExistsError(f"ya existe un sistema «{pid}» en tu catálogo: elige otro identificador")
    catalogo.catalogo(raiz).mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(prefix=OCULTA, dir=catalogo.catalogo(raiz)))
    try:
        c = catalogo.crear(pid, titulo, descripcion, raiz=temporal, familia=familia)
        de_la_base = set(base.archivos_del_sistema(c))
        m_base = base.leer_manifiesto(c)
        escritos: dict[str, str] = {}
        mapeados: list[dict] = []
        conservados: list[dict] = []
        fusionados: list[dict] = []
        avisos: list[str] = []
        for rel, datos in limpios.items():
            if rel == base.MANIFIESTO:
                continue
            dest, motivo = destino_de(rel)
            if dest in escritos:
                dest = _libre(dest, escritos, c)
            ruta = c / dest
            if dest in de_la_base and dest.startswith("config/") and dest.endswith(".json"):
                try:
                    actual = json.loads(ruta.read_text(encoding="utf-8"))
                    suyo = json.loads(datos.decode("utf-8"))
                    if isinstance(actual, dict) and isinstance(suyo, dict):
                        ruta.write_text(json.dumps(_fusionar(actual, suyo), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                        de_la_base.discard(dest)
                        escritos[dest] = rel
                        fusionados.append({"de": rel, "a": dest, "motivo": "JSON fusionado con el de la base: tus valores mandan"})
                        continue
                except (UnicodeDecodeError, ValueError):
                    pass
            sustituye = dest in de_la_base
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(datos)
            de_la_base.discard(dest)
            escritos[dest] = rel
            if sustituye:
                motivo = (motivo + "; " if motivo else "") + "sustituye la versión de arranque de la base"
            (mapeados if motivo or dest != rel else conservados).append({"de": rel, "a": dest, "motivo": motivo})
        if base.MANIFIESTO in limpios:
            if m_usuario:
                m, av = fusionar_manifiesto(m_base, m_usuario, pid, titulo)
                avisos += av
                errores_m = base.validar_manifiesto(m)
                if errores_m:
                    original = _libre("config/sistema.importado.json", escritos, c)
                    (c / original).parent.mkdir(parents=True, exist_ok=True)
                    (c / original).write_bytes(limpios[base.MANIFIESTO])
                    conservados.append({"de": base.MANIFIESTO, "a": original, "motivo": "no encaja en el formato del manifiesto: guardado tal cual"})
                    avisos.append(f"sistema.json no se pudo fusionar ({'; '.join(errores_m[:3])}): el original está en {original}")
                else:
                    catalogo._escribir_manifiesto(c, m)
                    fusionados.append({"de": base.MANIFIESTO, "a": base.MANIFIESTO, "motivo": "manifiesto fusionado con el de la base: tus valores mandan"})
            else:
                original = _libre("config/sistema.importado.json", escritos, c)
                (c / original).parent.mkdir(parents=True, exist_ok=True)
                (c / original).write_bytes(limpios[base.MANIFIESTO])
                conservados.append({"de": base.MANIFIESTO, "a": original, "motivo": "no es un JSON válido: guardado tal cual"})
            de_la_base.discard(base.MANIFIESTO)
        _declarar_extensiones(c, escritos)
        try:
            entrada.actualizar(c)
        except (OSError, ValueError, KeyError) as e:
            avisos.append(f"no se pudo regenerar el bloque de entrada: {e}")
        binarios = sorted(d for d, o in escritos.items() if not _es_texto(limpios[o]))
        if binarios:
            avisos.append(f"{len(binarios)} archivo(s) binario(s) se guardan en tu equipo; el borrador web solo admite texto")
        resumen = {
            "id": pid, "titulo": titulo, "aplicado": False, "ruta": None,
            "mapeados": mapeados, "fusionados": fusionados, "conservados": conservados,
            "de_la_base": sorted(r for r in de_la_base if not r.startswith("scripts/comun/")),
            "renombrados": renombrados, "ignorados": ignorados, "binarios": binarios,
            "archivos": base.archivos_del_sistema(c), "errores": esp.validar_sistema(c), "avisos": avisos,
            "total_importados": len(limpios),
        }
        if aplicar:
            if destino.exists():
                raise FileExistsError(f"ya existe {destino}")
            c.rename(destino)
            resumen.update(aplicado=True, ruta=str(destino))
        return resumen
    finally:
        shutil.rmtree(temporal, ignore_errors=True)


def _declarar_extensiones(c: Path, escritos: dict[str, str]) -> None:
    """Las carpetas y archivos de primer nivel que trajo la persona y no son núcleo ni pieza quedan declarados en
    «extensiones» (así el sistema valida sin moverlos ni borrarlos)."""
    m = base.leer_manifiesto(c)
    ext = dict(m.get("extensiones") or {})
    nuevos = False
    for p in sorted(c.iterdir()):
        if p.name in base.RESERVADOS or p.name in ext or p.name.startswith(".") or base.IGNORAR.search(p.name):
            continue
        origen = sorted({o.split("/")[0] for d, o in escritos.items() if d.split("/")[0] == p.name})
        ext[p.name] = f"Importado tal cual ({', '.join(origen) or p.name}): revisa para qué sirve"
        nuevos = True
    if nuevos:
        m["extensiones"] = ext
        catalogo._escribir_manifiesto(c, m)


def _con_sufijo(rel: str, n: int = 2) -> str:
    p = Path(rel)
    m = re.match(r"^(.*)-(\d+)$", p.stem)
    raiz, n = (m.group(1), int(m.group(2)) + 1) if m else (p.stem, n)
    return (p.parent / f"{raiz}-{n}{p.suffix}").as_posix().removeprefix("./")


def _libre(dest: str, escritos: dict, c: Path) -> str:
    while dest in escritos or (c / dest).exists() and dest in escritos.values():
        dest = _con_sufijo(dest)
    while dest in escritos:
        dest = _con_sufijo(dest)
    return dest


def _es_texto(datos: bytes) -> bool:
    if b"\x00" in datos:
        return False
    try:
        datos.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True
