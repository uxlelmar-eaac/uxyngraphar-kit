#!/usr/bin/env python3
"""Pruebas de las copias de seguridad: manifiesto, deshacer una actualización entera, política de limpieza, CLI y protección."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import respaldos as rs
from test_nucleo import Base, act, copiar_pack, lock  # noqa: F401 - Base no contiene pruebas propias

CLI = Path(__file__).resolve().parent.parent / "respaldos.py"


class TestDeshacerActualizacion(Base):
    def setUp(self) -> None:
        super().setUp()
        self.instalar()
        self.nuevo = copiar_pack(self.tmp / "pack2")
        v = lock.version_de(self.pack)
        f = self.nuevo / "VERSION.md"
        f.write_text(f.read_text(encoding="utf-8").replace(f"version: {v}", f"version: {lock.mayor(v)}.99.0", 1), encoding="utf-8")
        (self.nuevo / "REGLAS.md").write_text("regla nueva\n", encoding="utf-8")
        (self.nuevo / "10-guias" / "guia-nueva.md").write_text("# nueva\n", encoding="utf-8")

    def test_manifiesto_y_restaurar_todo(self) -> None:
        antes_reglas = (self.repo / "docs/REGLAS.md").read_text(encoding="utf-8")
        antes_lock = lock.leer(self.repo, "docs")
        carpeta = act.aplicar(self.nuevo, self.repo, "docs", act.planificar(self.nuevo, self.repo, "docs"))
        m = json.loads((carpeta / rs.MANIFIESTO).read_text(encoding="utf-8"))
        self.assertEqual(m["origen"], "actualizacion")
        self.assertIn("docs/REGLAS.md", m["archivos"])
        self.assertIn("docs/.uxyngraphar.lock", m["archivos"])
        self.assertIn("docs/10-guias/guia-nueva.md", m["añadidos"])
        r = rs.buscar(self.repo, "docs", f"actualizacion/{carpeta.name}")
        plan, previa = rs.restaurar(self.repo, "docs", r)
        self.assertEqual((self.repo / "docs/REGLAS.md").read_text(encoding="utf-8"), antes_reglas)
        self.assertEqual(lock.leer(self.repo, "docs")["version"], antes_lock["version"])
        self.assertFalse((self.repo / "docs/10-guias/guia-nueva.md").exists())
        self.assertTrue((previa / "docs/REGLAS.md").is_file())          # la restauración también se puede deshacer
        self.assertEqual(act.planificar(self.pack, self.repo, "docs").acciones, [])   # núcleo íntegro respecto al lock


class TestPolitica(Base):
    def _copia(self, origen: str, dias: int, n: int = 0) -> Path:
        raiz, _ = rs.raices(self.repo, "docs")[origen]
        fecha = datetime.now() - timedelta(days=dias)
        c = raiz / (fecha.strftime(rs.FORMATO_FECHA) + (f"-{n}" if n else ""))
        c.mkdir(parents=True)
        (c / "a.md").write_text("x", encoding="utf-8")
        (c / rs.MANIFIESTO).write_text(json.dumps({"origen": origen, "fecha": fecha.isoformat(timespec="seconds"), "archivos": ["a.md"]}), encoding="utf-8")
        return c

    def test_caducan_salvo_las_mas_recientes(self) -> None:
        for d in (40, 50, 60, 70):
            self._copia("actualizacion", d)
        self._copia("depuracion", 90)
        caducas = rs.caducados(self.repo, "docs")   # conservar 30 días, mínimo 3 por origen
        self.assertEqual([r.dias for r in caducas], [70])
        self.assertEqual(len(rs.limpiar(self.repo, "docs", aplicar=True)), 1)
        self.assertEqual(len(rs.listar(self.repo, "docs")), 4)
        self.assertEqual(len(rs.caducados(self.repo, "docs", dias=0, minimo=0)), 4)

    def test_copia_antigua_sin_manifiesto(self) -> None:
        c = rs.raices(self.repo, "docs")["actualizacion"][0] / "20200101-000000"
        (c / "docs").mkdir(parents=True)
        (c / "docs/REGLAS.md").write_text("vieja", encoding="utf-8")
        r = rs.buscar(self.repo, "docs", "20200101-000000")
        self.assertEqual(r.archivos, ["docs/REGLAS.md"])
        self.assertGreater(r.dias, 365)

    def test_cli_exige_humano_para_aplicar(self) -> None:
        self._copia("actualizacion", 400)
        for d in (1, 2, 3):
            self._copia("actualizacion", d)
        env = {k: v for k, v in os.environ.items() if k.upper() != "UXYNGRAPHAR_HUMANO"}
        base = [sys.executable, str(CLI), "limpiar", "--repo", str(self.repo)]
        r = subprocess.run(base + ["--aplicar"], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)
        self.assertEqual(r.returncode, 2, r.stdout)
        r = subprocess.run(base, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)
        self.assertIn("Se borrarían", r.stdout)
        r = subprocess.run(base + ["--aplicar"], capture_output=True, text=True, stdin=subprocess.DEVNULL, env={**env, "UXYNGRAPHAR_HUMANO": "1"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(len(rs.listar(self.repo, "docs")), 3)
        listado = subprocess.run([sys.executable, str(CLI), "listar", "--repo", str(self.repo)], capture_output=True, text=True)
        self.assertIn("Política: conservar 30 días", listado.stdout)


class TestProteccion(Base):
    def test_agente_no_lee_copias(self) -> None:
        self.instalar()
        import proteccion
        reglas = json.loads(proteccion.reglas_agente(self.repo, "docs").read_text(encoding="utf-8"))["permissions"]["deny"]
        self.assertIn("Read(.uxyngraphar-respaldo/**)", reglas)
        self.assertIn("Write(docs/.depuracion/respaldo/**)", reglas)
        gi = (self.repo / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".uxyngraphar-respaldo/", gi)
        self.assertIn("docs/.depuracion/respaldo/", gi)



class TestHayTerminal(unittest.TestCase):
    """La entrada redirigida a NUL/devnull (CI, agentes, subprocess.DEVNULL) no cuenta como una persona, tampoco en Windows."""

    def test_devnull_no_es_una_persona(self) -> None:
        from terminal import hay_terminal
        with open(os.devnull, encoding="utf-8") as nulo:
            self.assertFalse(hay_terminal(nulo))

    def test_sin_flujo_valido_no_es_una_persona(self) -> None:
        from terminal import hay_terminal
        self.assertFalse(hay_terminal(object()))   # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
