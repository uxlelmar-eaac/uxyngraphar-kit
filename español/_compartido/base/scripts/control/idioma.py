"""R-22 — idioma de los artefactos del producto (código, archivos, commits, ramas). Lo usa la puerta de control.

Solo mira el **código del producto** (nunca `docs/`) y solo las líneas **añadidas**: el legacy que no se toca no se
señala. Dos niveles de confianza:
  fiable      identificadores y nombres de archivo con caracteres no-ASCII → nivel `niveles.idioma`
  heurístico  palabras en español, identificadores mezclados, comentarios y textos en español → siempre aviso
Commits y ramas → nivel `niveles.commits`. Rutas en `idioma.legacy` → todo baja a aviso. Marca de línea para eximir:
`uxyngraphar:permitir-idioma`. Guía: docs/00-nucleo/politica-idioma.md
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
from pathlib import Path

MARCA = "uxyngraphar:permitir-idioma"
TIPOS_COMMIT = ("feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert")
COMMIT_RE = re.compile(rf"^(?:{'|'.join(TIPOS_COMMIT)})(?:\([a-z0-9][a-z0-9._/-]*\))?!?: \S.*$")
COMMIT_LIBRE = re.compile(r"^(?:Merge |Revert \"|fixup! |squash! |amend! )")
RAMAS_DEFECTO = rf"^(?:main|master|develop|HEAD|release/[\w.-]+|(?:{'|'.join(TIPOS_COMMIT)}|hotfix)/[a-z0-9][a-z0-9._-]*)$"
COMENTARIO_HASH = {".py", ".rb", ".ex", ".exs", ".sh", ".r", ".pl", ".yaml", ".yml", ".toml"}
TEST_RE = re.compile(r"(?:^|/)(?:tests?|__tests__|spec|fixtures?)/|(?:^|/)(?:test_[^/]*|[^/]*_test\.\w+|[^/]*\.(?:test|spec)\.\w+)$")

# Palabras sin homónimo en inglés: evitan falsos positivos. Ampliable vía glosario (lo registrado no se señala).
ES = set("""obtener crear guardar borrar eliminar actualizar buscar listar validar calcular enviar cargar consultar registrar
generar procesar agregar quitar cambiar mostrar ocultar abrir cerrar iniciar terminar recibir asignar verificar
usuario usuarios cliente clientes factura facturas pago pagos nombre nombres apellido fecha fechas hora datos dato lista
cuenta cuentas correo contrasena clave precio precios cantidad monto saldo pedido pedidos producto productos proveedor
proveedores empleado empleados direccion telefono ciudad estado activo activa nuevo nueva numero importe impuesto
descuento tienda venta ventas compra compras inventario almacen sucursal empresa perfil mensaje mensajes respuesta
solicitud archivo archivos carpeta pagina boton ventana registro registros sesion permiso permisos tarea tareas
resultado resultados entrada salida valor valores tipo tipos codigo usuaria correcto incorrecto vacio lleno""".split())
EN = set("""get set is has can should by id list map data info user users item items count total new old to from with of for
on in at create update delete find load save send build parse handle init config service controller repository helper
util utils type value key name""".split())
STOP_ES = set("el la los las del que para por con una uno este esta estos cuando pero como se lo al es debe porque".split())

_CADENA = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`(?:[^`\\]|\\.)*`')
_TOKEN = re.compile(r"[^\W\d]\w*")
_NO_ASCII = re.compile(r"[^\x00-\x7f]")
_LETRA_ES = re.compile(r"[áéíóúüñÁÉÍÓÚÜÑ¿¡]")


def coincide(ruta: str, patrones: list[str]) -> bool:
    nombre = Path(ruta).name
    for p in patrones:
        if fnmatch.fnmatch(ruta, p) or fnmatch.fnmatch(nombre, p) or fnmatch.fnmatch("/" + ruta, "/" + p.lstrip("/")):
            return True
        if p.startswith("**/") and (fnmatch.fnmatch(ruta, p[3:]) or fnmatch.fnmatch("/" + ruta, "*/" + p[3:])):
            return True
    return False


def palabras(identificador: str) -> list[str]:
    """`obtenerUserById` → ['obtener', 'user', 'by', 'id']; `retencion_fiscal` → ['retencion', 'fiscal']."""
    trozos = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", identificador))
    return [w.lower() for w in re.split(r"[\s_\-]+", trozos) if w]


def glosario(repo: Path, docs: str, cfg: dict) -> set[str]:
    """Términos de dominio registrados (primera columna de las tablas del glosario) y sus palabras."""
    archivo = repo / docs / cfg.get("idioma", {}).get("glosario", "00-nucleo/glosario-dominio.md")
    terminos: set[str] = set()
    try:
        texto = archivo.read_text(encoding="utf-8")
    except OSError:
        return terminos
    for linea in texto.splitlines():
        celdas = [c.strip().strip("`") for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 2 or not celdas[0] or set(celdas[0]) <= set("-: ") or celdas[0].lower() in ("término", "termino", "term"):
            continue
        terminos.add(celdas[0].lower())
        terminos.update(palabras(celdas[0]))
    return terminos


def separar(linea: str, sufijo: str) -> tuple[str, list[str], str]:
    """(código sin cadenas ni comentario, cadenas, comentario). Heurística de una línea, suficiente para avisar."""
    cadenas = [m.group(0)[1:-1] for m in _CADENA.finditer(linea)]
    codigo = _CADENA.sub('""', linea)
    comentario = ""
    marcas = ["//", "/*", "<!--"] + (["#"] if sufijo in COMENTARIO_HASH else []) + (["--"] if sufijo == ".sql" else [])
    corte = min((i for i in (codigo.find(m) for m in marcas) if i >= 0), default=-1)
    if corte >= 0:
        codigo, comentario = codigo[:corte], codigo[corte:]
    elif codigo.lstrip().startswith("*"):   # cuerpo de comentario de bloque
        codigo, comentario = "", codigo
    return codigo, cadenas, comentario


def revisar_linea(ruta: str, linea: str, permitidos: set[str]) -> tuple[list[str], list[str]]:
    """(hallazgos fiables, hallazgos heurísticos) de una línea añadida."""
    fiables: list[str] = []
    heur: list[str] = []
    if MARCA in linea:
        return fiables, heur
    codigo, cadenas, comentario = separar(linea, Path(ruta).suffix.lower())
    for tok in dict.fromkeys(_TOKEN.findall(codigo)):
        if _NO_ASCII.search(tok):
            fiables.append(f"identificador no-ASCII «{tok}»: translitéralo a ASCII y en inglés (o término del glosario)")
            continue
        ws = palabras(tok)
        es = [w for w in ws if w in ES and w not in permitidos and tok.lower() not in permitidos]
        if es and any(w in EN for w in ws):
            heur.append(f"identificador mezclado «{tok}» (español + inglés): usa solo inglés")
        elif es:
            heur.append(f"identificador en español «{tok}»: tradúcelo o registra el término en el glosario de dominio")
    if comentario and (_LETRA_ES.search(comentario) or len(STOP_ES & set(re.findall(r"[a-záéíóúñ]+", comentario.lower()))) >= 2):
        heur.append("comentario en español: los comentarios van en inglés y explican el porqué")
    if not TEST_RE.search(ruta) and any(_LETRA_ES.search(c) for c in cadenas):
        heur.append("texto en español dentro del código: logs y errores técnicos en inglés; texto para el usuario final, por i18n con clave en inglés")
    return fiables, heur


def control_idioma(repo: Path, cambiados: list[str], nuevos: list[str], anadidas: dict[str, list[str]], cfg: dict, docs: str, es_codigo) -> list[tuple[str, str]]:
    """[(nivel, mensaje)]. `es_codigo(ruta)` decide qué es código del producto."""
    nivel = cfg["niveles"].get("idioma", "aviso")
    if nivel == "apagado":
        return []
    idi = cfg.get("idioma", {})
    excluir, legacy, locales = idi.get("excluir", []), idi.get("legacy", []), idi.get("locales", [])
    permitidos = glosario(repo, docs, cfg)
    salida: list[tuple[str, str]] = []

    def anotar(ruta: str, fiable: bool, msg: str) -> None:
        n = nivel if fiable and not coincide(ruta, legacy) else "aviso"
        salida.append((n, f"{ruta}: {msg} (R-22)"))

    for ruta in nuevos:   # nombres de archivo y carpeta nuevos, fuera de docs/
        if ruta.startswith((docs + "/", ".github/", ".claude/")) or coincide(ruta, excluir) or coincide(ruta, locales):
            continue
        if _NO_ASCII.search(ruta):
            anotar(ruta, True, "nombre de archivo o carpeta con caracteres no-ASCII")
        elif any(w in ES and w not in permitidos for w in palabras(Path(ruta).stem)):
            anotar(ruta, False, "nombre de archivo en español: los archivos nuevos se nombran en inglés")
    for ruta in cambiados:
        if not es_codigo(ruta) or coincide(ruta, excluir):
            continue
        fiables: list[str] = []
        heur: list[str] = []
        for linea in anadidas.get(ruta, []):
            f, h = revisar_linea(ruta, linea, permitidos)
            fiables += [x for x in f if x not in fiables]
            heur += [x for x in h if x not in heur]
        for m in fiables:
            anotar(ruta, True, m)
        for m in heur[:5]:
            anotar(ruta, False, m)
    return salida


def revisar_mensaje(texto: str) -> list[str]:
    """Problemas del asunto de un commit (Conventional Commits, inglés, ASCII)."""
    asunto = next((l.strip() for l in texto.splitlines() if l.strip() and not l.startswith("#")), "")
    if not asunto or COMMIT_LIBRE.match(asunto):
        return []
    problemas = []
    if not COMMIT_RE.match(asunto):
        problemas.append(f"«{asunto[:72]}» no sigue Conventional Commits: tipo(alcance): descripción en imperativo (p. ej. feat(billing): add refund endpoint)")
    if _NO_ASCII.search(asunto) or len(STOP_ES & set(re.findall(r"[a-záéíóúñ]+", asunto.lower()))) >= 2 or any(w in ES for w in re.findall(r"[a-z]+", asunto.lower())):
        problemas.append(f"«{asunto[:72]}» parece en español: los mensajes de commit van en inglés")
    return problemas


def revisar_rama(rama: str, cfg: dict) -> list[str]:
    patron = cfg.get("idioma", {}).get("ramas") or RAMAS_DEFECTO
    if not rama or re.match(patron, rama):
        return []
    return [f"rama «{rama}» no sigue tipo/alcance-descripcion en inglés y minúsculas (p. ej. feat/billing-add-refund)"]


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else ""


def archivos_nuevos(repo: Path, base: str | None, staged: bool) -> list[str]:
    args = ["diff", "--cached", "--name-only", "--diff-filter=AR"] if staged else ["diff", "--name-only", "--diff-filter=AR", f"{base}...HEAD"]
    return [l for l in _git(repo, *args).splitlines() if l]


def asuntos_commits(repo: Path, base: str) -> list[str]:
    return [l for l in _git(repo, "log", "--no-merges", "--format=%s", f"{base}..HEAD").splitlines() if l]


def rama_actual(repo: Path) -> str:
    return _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
