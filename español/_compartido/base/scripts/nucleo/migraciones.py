"""Migraciones entre versiones: los cambios que una versión necesita hacer en un proyecto ya instalado.

Cuando una versión renombra o mueve algo que el proyecto ya tiene (una clave de uxyngraphar.config.json, un archivo,
una carpeta), lo hace aquí, en código, en lugar de pedírselo a la persona. Así actualizar sigue siendo un solo paso.

Reglas para escribir una migración (las comprueba test_transaccion.py):
  · `version` es la versión que la trae; se aplica al pasar de una versión anterior a ella o a una posterior.
  · Idempotente: si ya está hecha (o no hay nada que migrar), no cambia nada y devuelve [].
  · Solo usa los métodos de `Contexto` (todo pasa por la transacción: copia de seguridad y vuelta atrás automática).
  · Nunca borra contenido del proyecto: lo mueve o lo transforma.
  · Una vez publicada no se edita ni se quita: el lock de cada proyecto guarda los ids aplicados.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import clasificacion as cl
import lock
from transaccion import Transaccion


class Contexto:
    """Lo que una migración puede hacer en el proyecto. Rutas relativas a docs/ (o «/AGENTES.md» para la raíz de la app)."""

    def __init__(self, repo: Path, docs: str, tx: Transaccion) -> None:
        self.repo, self.docs, self.tx = repo, docs, tx

    def _rel(self, ruta: str) -> str:
        return cl.destino(ruta[1:], self.docs) if ruta.startswith("/") else f"{self.docs}/{ruta}"

    def existe(self, ruta: str) -> bool:
        return (self.repo / self._rel(ruta)).exists()

    def leer(self, ruta: str) -> str | None:
        f = self.repo / self._rel(ruta)
        return f.read_text(encoding="utf-8") if f.is_file() else None

    def escribir(self, ruta: str, texto: str) -> None:
        self.tx.escribir(self._rel(ruta), texto.encode("utf-8"))

    def mover(self, desde: str, hacia: str) -> bool:
        """Mueve un archivo si existe el origen y no el destino. True si lo movió."""
        origen, destino = self.repo / self._rel(desde), self.repo / self._rel(hacia)
        if not origen.is_file() or destino.exists():
            return False
        self.tx.copiar(self._rel(hacia), origen)
        self.tx.borrar(self._rel(desde))
        return True

    def config(self) -> dict | None:
        """El uxyngraphar.config.json del proyecto tal cual (sin valores por defecto), o None si no existe o no se puede leer."""
        texto = self.leer("uxyngraphar.config.json")
        try:
            datos = json.loads(texto) if texto is not None else None
        except ValueError:
            return None
        return datos if isinstance(datos, dict) else None

    def guardar_config(self, datos: dict) -> None:
        self.escribir("uxyngraphar.config.json", json.dumps(datos, ensure_ascii=False, indent=2) + "\n")

    def preparar_repo(self, rel: str) -> bytes | None:
        """Para archivos de la raíz del repo git (.claude/, .github/, exclusiones): guarda su copia en la transacción
        antes de que otra función los reescriba. Devuelve el contenido actual (None si no existe)."""
        self.tx.preparar(rel)
        f = self.repo / rel
        return f.read_bytes() if f.is_file() else None


@dataclass(frozen=True)
class Migracion:
    version: str
    id: str
    descripcion: str
    aplicar: Callable[[Contexto], list[str]]   # devuelve qué hizo, en frases cortas; [] si no había nada que hacer


# Registro en orden de versión. Vacío en la línea base 1.0.0: la primera versión publicada ya instala todo en su
# forma final (memoria fuera del alcance de la IA, 96-reglas-proyecto, sección reglas_proyecto…), así que no hay nada
# que migrar. La primera migración llegará con la versión que cambie algo ya instalado.
REGISTRO: list[Migracion] = []


def pendientes(adoptada: str, nueva: str, hechas: set[str], registro: list[Migracion] | None = None) -> list[Migracion]:
    """Las migraciones que tocan en este salto y aún no se aplicaron. Versión adoptada desconocida: todas (son idempotentes)."""
    registro = REGISTRO if registro is None else registro
    desde, hasta = lock._tupla(adoptada), lock._tupla(nueva)
    conocida = adoptada not in ("", "desconocida")
    salida = [m for m in registro if m.id not in hechas and lock._tupla(m.version) <= hasta and (not conocida or lock._tupla(m.version) > desde)]
    return sorted(salida, key=lambda m: lock._tupla(m.version))


def ejecutar(lista: list[Migracion], repo: Path, docs: str, tx: Transaccion) -> list[tuple[str, list[str]]]:
    ctx = Contexto(repo, docs, tx)
    return [(m.id, m.aplicar(ctx)) for m in lista]
