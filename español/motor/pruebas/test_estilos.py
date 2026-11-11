"""Pruebas del núcleo visual del panel: todo color y toda tipografía de `web/` salen de los 20 primitivos y de los
tokens de fuente, con los mismos valores que `src/common/styles/globals.css` del frontend y la landing."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import _rutas  # noqa: F401

WEB = Path(__file__).resolve().parents[1] / "web"
ESTILOS = WEB / "estilos.css"

PRIMITIVOS = {
    "--color-ink": "#0b0d12", "--color-depth": "#06070a", "--color-brand": "#3d5afe", "--color-brand-alt": "#8a93a6",
    "--color-tone": "#ff6b1a", "--color-canvas": "#f4f5f7", "--color-surface": "#e6e8ee", "--color-edge": "#ffffff",
    "--color-affirm": "#19d27a", "--color-signal": "#d82525",
    "--color-on-ink": "#f4f5f7", "--color-on-depth": "#eceef2", "--color-on-brand": "#ffffff", "--color-on-brand-alt": "#0b0d12",
    "--color-on-tone": "#0b0d12", "--color-on-canvas": "#0b0d12", "--color-on-surface": "#0b0d12", "--color-on-edge": "#0b0d12",
    "--color-on-affirm": "#0b0d12", "--color-on-signal": "#ffffff",
}
FAMILIAS = {"--font-heading": "'Poppins'", "--font-body": "'Inter'", "--font-accent": "'Montserrat'"}
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
DECLARACION = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")


def expandir(hex_: str) -> str:
    h = hex_.lower()
    return "#" + "".join(c * 2 for c in h[1:]) if len(h) == 4 else h


def sin_comentarios(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


class EstilosDelPanel(unittest.TestCase):
    def setUp(self):
        self.css = sin_comentarios(ESTILOS.read_text(encoding="utf-8"))
        self.tokens = dict(DECLARACION.findall(self.css))

    def test_los_primitivos_coinciden_con_los_de_las_apps(self):
        for clave, valor in PRIMITIVOS.items():
            self.assertEqual(self.tokens.get(clave, "").strip().lower(), valor, clave)

    def test_solo_los_primitivos_escriben_hex(self):
        fugas = [linea.strip() for linea in self.css.splitlines()
                 if HEX.search(linea) and not re.match(r"\s*--color-(on-)?[a-z-]+\s*:\s*#[0-9a-fA-F]{6};\s*$", linea)]
        self.assertEqual(fugas, [])

    def test_no_hay_colores_por_funcion_ni_por_nombre(self):
        fugas = re.findall(r"\b(?:rgba?|hsla?|hwb|oklch|oklab)\(|:\s*(?:white|black)\b", self.css)
        self.assertEqual(fugas, [])

    def test_la_tipografia_sale_de_los_tokens(self):
        for clave, familia in FAMILIAS.items():
            self.assertTrue(self.tokens.get(clave, "").startswith(familia), clave)
        reglas = re.sub(r"@font-face\s*\{[^}]*\}", "", self.css)   # sus descriptores declaran la fuente, no la aplican
        fugas = []
        for prop, valor in re.findall(r"(?<![-\w])(font-family|font-size|font-weight|line-height|font)\s*:\s*([^;}]+)", reglas):
            if valor.strip() != "inherit" and not re.fullmatch(r"var\(--(font|line-height)-[a-z0-9-]+\)", valor.strip()):
                fugas.append(f"{prop}: {valor.strip()}")
        self.assertEqual(fugas, [])

    def test_las_fuentes_estan_empaquetadas_con_su_licencia(self):
        for url in re.findall(r"url\('([^']+)'\)", self.css):
            self.assertTrue((WEB / url).is_file(), url)
        for familia in ("inter", "poppins", "montserrat"):
            self.assertTrue((WEB / "fuentes" / f"OFL-{familia}.txt").is_file(), familia)

    def test_el_icono_usa_solo_la_paleta(self):
        paleta = set(PRIMITIVOS.values())
        fuera = {expandir(h) for h in HEX.findall((WEB / "icono.svg").read_text(encoding="utf-8"))} - paleta
        self.assertEqual(fuera, set())


if __name__ == "__main__":
    unittest.main()
