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
    "--color-ink": "#121002", "--color-depth": "#0b0a01", "--color-brand": "#b8a018", "--color-brand-alt": "#a6a07e",
    "--color-tone": "#e84800", "--color-canvas": "#fbfaf3", "--color-surface": "#f6f4e3", "--color-edge": "#fefdfa",
    "--color-affirm": "#00a870", "--color-signal": "#cc1600",
    "--color-on-ink": "#fefdfa", "--color-on-depth": "#fefdfa", "--color-on-brand": "#121002", "--color-on-brand-alt": "#121002",
    "--color-on-tone": "#121002", "--color-on-canvas": "#121002", "--color-on-surface": "#121002", "--color-on-edge": "#121002",
    "--color-on-affirm": "#121002", "--color-on-signal": "#fefdfa",
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
        # estilos.css y las hojas de cada sección (flujos.css…): todas siguen las mismas reglas
        hojas = [ESTILOS] + sorted(p for p in WEB.glob("*.css") if p != ESTILOS)
        self.css = sin_comentarios("\n".join(p.read_text(encoding="utf-8") for p in hojas))
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

    def test_el_icono_es_la_marca_oficial_png(self):
        """El panel y los accesos usan la PNG oficial (Logo-uxyngraphar), no un SVG inventado."""
        icono = WEB / "icono.png"
        self.assertTrue(icono.is_file(), "falta web/icono.png")
        self.assertEqual(icono.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertFalse((WEB / "icono.svg").exists(), "no debe quedar un icono.svg inventado")


if __name__ == "__main__":
    unittest.main()
