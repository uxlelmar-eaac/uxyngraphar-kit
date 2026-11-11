"""Pruebas normativas sobre la documentación: que no contradiga la norma ni el código (status prohibidos en ejemplos,
líneas de instalación, enlaces)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote

import _rutas  # noqa: F401

MOTOR = Path(__file__).resolve().parents[1]
ES = MOTOR.parent
KIT = ES.parent
NORMATIVOS = [MOTOR / n for n in ("ESPECIFICACION.md", "GUIA-DE-SISTEMAS.md", "GENERADOR.md", "GUIA-PARA-AGENTES.md", "README.md")]
NORMATIVOS += sorted((ES / "sistemas-de-gobernanza" / "_base").rglob("*.md"))
PROHIBIDOS = re.compile(r"\b(approved|archived|pending|done|draft|rejected|cancelled|superseded|deprecated|authorized|revoked)\b")


def lineas_instalacion(texto: str) -> list[str]:
    return sorted({m.group(0).strip() for m in re.finditer(r"(?:curl|irm) [^\n]*instalar-uxyngraphar\.py \| (?:python3|py) -", texto)})


ENLACE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def enlaces_rotos(md: Path) -> list[str]:
    """Enlaces relativos de un .md que apuntan a un archivo o carpeta que no existe (ignora URLs, anclas y marcadores)."""
    salida = []
    texto = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    for destino in ENLACE.findall(texto):
        destino = destino.split("#", 1)[0]
        if not destino or re.match(r"^[a-z]+:", destino) or "{" in destino or "<" in destino or destino.startswith("/"):
            continue
        if not (md.parent / unquote(destino)).exists():
            salida.append(destino)
    return salida


def prohibidos_fuera_de_norma(texto: str) -> list[str]:
    """Status de la columna «No usar» fuera de las tablas de la norma y de la sección de heredados."""
    salida = []
    for n, linea in enumerate(texto.splitlines(), 1):
        if "No usar" in linea or "heredad" in linea.lower():
            continue
        salida += [f"{n}: {m.group(0)}" for m in PROHIBIDOS.finditer(linea)]
    return salida


class TestDocumentacion(unittest.TestCase):
    def test_sin_status_prohibidos_en_los_ejemplos(self):   # C-21
        for ruta in NORMATIVOS:
            with self.subTest(ruta.name):
                self.assertEqual(prohibidos_fuera_de_norma(ruta.read_text(encoding="utf-8")), [], ruta)

    def test_detecta_un_status_prohibido(self):
        self.assertEqual(prohibidos_fuera_de_norma("p. ej. `approved` → `scripts/ciclo.py aprobar`"), ["1: approved"])

    def test_lineas_de_instalacion_del_readme(self):   # C-24
        readme = lineas_instalacion((KIT / "README.md").read_text(encoding="utf-8"))
        instalador = lineas_instalacion((MOTOR / "distribucion" / "arranque_descarga.py").read_text(encoding="utf-8"))
        self.assertEqual(len(instalador), 2, "Linux/macOS y Windows")
        self.assertEqual(readme, instalador)

    def test_enlaces_relativos_existen(self):   # M-20
        rotos = {}
        for md in sorted([*KIT.glob("*.md"), *ES.rglob("*.md")]):
            if "__pycache__" in md.parts or "andamiaje" in md.parts:
                continue
            malos = enlaces_rotos(md)
            if malos:
                rotos[md.relative_to(KIT).as_posix()] = malos
        self.assertEqual(rotos, {})

    def test_detecta_un_enlace_roto(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            md = Path(t) / "a.md"
            md.write_text("[bien](a.md) [mal](no-existe.md) [web](https://x.org) [ancla](#y)\n", encoding="utf-8")
            self.assertEqual(enlaces_rotos(md), ["no-existe.md"])

    def test_changelog_al_dia_con_version(self):   # M-20
        version = (MOTOR / "VERSION").read_text(encoding="utf-8").strip()
        primera = re.search(r"^## (\S+)", (MOTOR / "CHANGELOG.md").read_text(encoding="utf-8"), re.M).group(1)
        self.assertEqual(primera, version)

    def test_la_skill_crear_sistema_cita_comandos_que_existen(self):   # M-19
        import cli
        texto = (MOTOR / "skills" / "crear-sistema" / "SKILL.md").read_text(encoding="utf-8")
        comandos = set(cli.analizador()._subparsers._group_actions[0].choices)
        citados = set(re.findall(r"\$U ([a-z][a-z-]+)", texto))
        self.assertTrue(citados)
        self.assertEqual(citados - comandos, set())
        gen = set(cli.analizador()._subparsers._group_actions[0].choices["generar"]._subparsers._group_actions[0].choices)
        self.assertEqual(set(re.findall(r"\$U generar ([a-z]+)", texto)) - gen, set())


if __name__ == "__main__":
    unittest.main()
