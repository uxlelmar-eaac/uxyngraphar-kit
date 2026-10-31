"""Cómo se ve uxyngraphar en la terminal: colores, marcas (✓ ! ✕) y tablas que se ajustan al ancho.

Solo biblioteca estándar. El color se usa únicamente si la salida es una terminal, NO_COLOR no está definida
y TERM no es «dumb»; si la terminal no puede escribir ✓/✕, se usan equivalentes ASCII.
El instalador de una línea (arranque_descarga.py) lleva su propia copia mínima de esto, porque se publica
como un único archivo sin acceso a este módulo: si cambias las marcas o los colores, cámbialos allí también.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import textwrap

MARCAS = {"ok": "✓", "aviso": "!", "error": "✕", "paso": "•"}
MARCAS_ASCII = {"ok": "+", "aviso": "!", "error": "x", "paso": "-"}
COLORES = {"ok": "32", "aviso": "33", "error": "31", "paso": "2", "titulo": "1", "seccion": "1;36", "dim": "2", "comando": "36"}
ANSI = re.compile(r"\x1b\[[0-9;]*m")
ANCHO_MAXIMO = 110

_vt_windows: bool | None = None


def _activar_vt_windows() -> bool:
    """En Windows 10+ un os.system("") vacío activa las secuencias de color de la consola."""
    global _vt_windows
    if _vt_windows is None:
        try:
            os.system("")
            _vt_windows = True
        except Exception:  # noqa: BLE001 - sin color es una salida válida
            _vt_windows = False
    return _vt_windows


def color_activo(flujo=None) -> bool:
    flujo = flujo or sys.stdout
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    try:
        if not flujo.isatty():
            return False
    except (AttributeError, ValueError):
        return False
    return _activar_vt_windows() if os.name == "nt" else True


def sin_color(texto: str) -> str:
    return ANSI.sub("", texto)


def pintar(texto: str, tipo: str, flujo=None) -> str:
    if not texto or tipo not in COLORES or not color_activo(flujo):
        return texto
    return f"\x1b[{COLORES[tipo]}m{texto}\x1b[0m"


def marca(tipo: str, flujo=None) -> str:
    """La marca de un estado (ok, aviso, error, paso), con su color y en ASCII si la terminal no puede escribirla."""
    flujo = flujo or sys.stdout
    simbolo = MARCAS.get(tipo, "·")
    try:
        simbolo.encode(getattr(flujo, "encoding", None) or "utf-8")
    except (UnicodeEncodeError, LookupError):
        simbolo = MARCAS_ASCII.get(tipo, "-")
    return pintar(simbolo, tipo, flujo)


def ancho_terminal() -> int:
    return max(40, min(shutil.get_terminal_size((100, 24)).columns, ANCHO_MAXIMO))


# ---------- textos en línea (devuelven la cadena) ----------

def dim(texto: str) -> str:
    return pintar(texto, "dim")


def comando(texto: str) -> str:
    return pintar(texto, "comando")


def linea(tipo: str, texto: str, sangria: str = "  ", flujo=None) -> str:
    """«  ✓ texto»: marca de color y el texto; los errores y avisos colorean también el texto."""
    cuerpo = pintar(texto, tipo, flujo) if tipo in ("error", "aviso") else texto
    return f"{sangria}{marca(tipo, flujo)} {cuerpo}"


# ---------- impresión ----------

def titulo(texto: str) -> None:
    print(pintar(texto, "titulo"))


def seccion(texto: str) -> None:
    print("\n" + pintar(texto, "seccion"))


def ok(texto: str, sangria: str = "  ") -> None:
    print(linea("ok", texto, sangria))


def aviso(texto: str, sangria: str = "  ") -> None:
    print(linea("aviso", texto, sangria))


def paso(texto: str, sangria: str = "  ") -> None:
    print(linea("paso", texto, sangria))


def error(texto: str, sangria: str = "") -> None:
    print(linea("error", texto, sangria, sys.stderr), file=sys.stderr)


# ---------- tablas ----------

def tabla(filas: list[tuple[str, str]], sangria: int = 2, separacion: int = 3, ancho: int | None = None,
          izquierda: int | None = None) -> list[str]:
    """Dos columnas alineadas: la izquierda (un comando) en color y la derecha ajustada al ancho con sangría colgante.

    Si una entrada de la izquierda es demasiado larga, su descripción empieza en la línea siguiente.
    «izquierda» fija el ancho de la primera columna (para alinear varias tablas seguidas).
    Devuelve las líneas para que quien llama decida dónde imprimirlas.
    """
    ancho = ancho or ancho_terminal()
    tope = max(12, ancho * 2 // 5)
    izquierda = min(izquierda or max((len(a) for a, _ in filas), default=0), tope)
    columna = sangria + izquierda + separacion
    envoltura = max(20, ancho - columna)
    salida = []
    for a, b in filas:
        partes = textwrap.wrap(b, envoltura) or [""]
        prefijo = " " * sangria + comando(a)
        if len(a) > izquierda:
            salida.append(prefijo)
            salida.extend(" " * columna + p for p in partes)
            continue
        salida.append(prefijo + " " * (izquierda - len(a) + separacion) + partes[0])
        salida.extend(" " * columna + p for p in partes[1:])
    return salida
