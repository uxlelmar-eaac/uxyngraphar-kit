"""1.6.4: la revisión de archivos colorea cada ruta según su capa de uxyngraphar (núcleo, estándar, común o propio).

Las listas de la vista (`estructura-sistema.js`) son las de `_base/scripts/comun/uxyn_base.py`: si el protocolo cambia
sus piezas o su núcleo, esta prueba avisa."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import especificacion as esp

WEB = Path(__file__).resolve().parents[1] / "web"
ESTRUCTURA = WEB / "js" / "vistas" / "estructura-sistema.js"


def lista_js(nombre: str) -> list[str]:
    m = re.search(rf"export const {nombre} = \[(.*?)\];", ESTRUCTURA.read_text(encoding="utf-8"), re.S)
    assert m, nombre
    return re.findall(r'"([^"]+)"', m.group(1))


class TestCapas(unittest.TestCase):
    def test_listas_iguales_al_protocolo(self):
        base = esp.base
        self.assertEqual(set(lista_js("NUCLEO")), {*base.NUCLEO, base.INTEGRIDAD})
        self.assertEqual(set(lista_js("PIEZAS")), set(base.PIEZAS.values()))
        self.assertIn(f'export const COMUN = "{esp.DESTINO_COMUN}"', ESTRUCTURA.read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "sin node")
    def test_capa_de_cada_ruta(self):
        codigo = (
            f"import {{ capaDe, contarCapas }} from {json.dumps(ESTRUCTURA.as_uri())};"
            "const r = ['LIMITES.md','proceso/diagnosticar.md','skills','scripts/comun/memorias.py','scripts',"
            "'config/ajustes.json','prompts/agente.md','CHANGELOG.md','INTEGRIDAD.json'];"
            "console.log(JSON.stringify([r.map(capaDe), contarCapas(r)]));"
        )
        salida = subprocess.run(["node", "--input-type=module", "-e", codigo], capture_output=True, text=True, check=True)
        capas, cuenta = json.loads(salida.stdout)
        self.assertEqual(capas, ["nucleo", "estandar", "estandar", "comun", "comun", "propio", "propio", "estandar", "nucleo"])
        self.assertEqual(cuenta, {"nucleo": 2, "estandar": 3, "comun": 2, "propio": 2})

    def test_la_revision_pinta_capas_y_leyenda(self):
        js = (WEB / "js" / "vistas" / "revision.js").read_text(encoding="utf-8")
        for trozo in ("capa-${capaDe(rel)}", "capas-leyenda", "capa-insignia"):
            self.assertIn(trozo, js)
        css = (WEB / "estilos.css").read_text(encoding="utf-8")
        for token in ("--capa-nucleo", "--capa-estandar", "--capa-comun", ".capas-leyenda"):
            self.assertIn(token, css)


if __name__ == "__main__":
    unittest.main()
