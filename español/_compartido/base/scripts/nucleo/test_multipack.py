"""Varios packs en un mismo repositorio (apps/api/docs + apps/web/docs) y packs en repos separados."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PACKS = AQUI.parents[2]          # español/
sys.path.insert(0, str(AQUI))

if not (PACKS / "backend" / "AGENTES.md").is_file():   # instalado en un proyecto: faltan los packs fuente hermanos
    raise unittest.SkipTest("requiere el repo fuente de uxyngraphar (español/backend y español/frontend); se omite en un proyecto instalado")
sys.path.insert(0, str(AQUI.parent / "ganchos"))

import clasificacion as cl  # noqa: E402


def instalar_pack(rol: str, repo: Path, docs: str, *extra: str) -> subprocess.CompletedProcess:
    pack = PACKS / ("backend" if rol == "servidor" else "frontend")
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(pack / "scripts" / "instalar-pack.py"), str(pack), "--repo", str(repo), "--docs", docs, *extra], capture_output=True, text=True)


class TestRutas(unittest.TestCase):
    def test_destino_y_origen_con_carpeta_de_app(self):
        self.assertEqual(cl.destino("AGENTES.md", "docs"), "AGENTES.md")
        self.assertEqual(cl.destino("AGENTES.md", "apps/api/docs"), "apps/api/AGENTES.md")
        self.assertEqual(cl.destino("REGLAS.md", "apps/api/docs"), "apps/api/docs/REGLAS.md")
        self.assertEqual(cl.origen("apps/api/AGENTES.md", "apps/api/docs"), "AGENTES.md")
        self.assertEqual(cl.origen("AGENTES.md", "apps/api/docs"), None)
        self.assertEqual(cl.origen("apps/api/docs/REGLAS.md", "apps/api/docs"), "REGLAS.md")


class TestMismoRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Se instala una sola vez (es lo lento); las pruebas se ordenan para que la que altera el núcleo corra al final."""
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=cls.repo, check=True)
        (cls.repo / "apps/api").mkdir(parents=True)
        (cls.repo / "apps/web").mkdir(parents=True)
        (cls.repo / "apps/api/pyproject.toml").write_text("[project]\n")
        (cls.repo / "apps/web/package.json").write_text('{"dependencies":{"react":"18"}}')
        r1 = instalar_pack("servidor", cls.repo, "apps/api/docs", "--proteger", "--propietario", "@a", "--claude-md")
        r2 = instalar_pack("cliente", cls.repo, "apps/web/docs", "--proteger", "--propietario", "@b", "--claude-md")
        assert (r1.returncode, r2.returncode) == (0, 0), r1.stdout + r1.stderr + r2.stdout + r2.stderr

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def instalar_ambos(self):
        pass

    def test_cada_app_tiene_su_agentes_sin_conflicto(self):
        self.instalar_ambos()
        for app in ("api", "web"):
            for f in ("AGENTES.md", "AGENTS.md", "CLAUDE.md", "docs/.uxyngraphar.lock", "docs/uxyngraphar.config.json"):
                self.assertTrue((self.repo / "apps" / app / f).is_file(), f"{app}/{f}")
        self.assertIn("servidor", (self.repo / "apps/api/AGENTES.md").read_text().splitlines()[0])
        self.assertIn("cliente", (self.repo / "apps/web/AGENTES.md").read_text().splitlines()[0])
        self.assertFalse(list(self.repo.rglob("*.uxyngraphar-nuevo")))
        self.assertFalse((self.repo / "AGENTES.md").exists())

    def test_config_limita_el_control_al_codigo_de_cada_app(self):
        self.instalar_ambos()
        import json
        api = json.loads((self.repo / "apps/api/docs/uxyngraphar.config.json").read_text())
        web = json.loads((self.repo / "apps/web/docs/uxyngraphar.config.json").read_text())
        self.assertEqual((api["rol"], web["rol"]), ("servidor", "cliente"))
        self.assertTrue(all(r.startswith("apps/api") for r in api["codigo"]["raices"]), api["codigo"])
        self.assertTrue(all(r.startswith("apps/web") for r in web["codigo"]["raices"]), web["codigo"])

    def test_nucleo_integro_en_ambos_y_deteccion_de_alteracion_en_uno(self):
        self.instalar_ambos()
        for app in ("api", "web"):
            pack = PACKS / ("backend" if app == "api" else "frontend")
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(pack / "scripts" / "verificar-nucleo.py"), "--docs", f"apps/{app}/docs"], cwd=self.repo, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (self.repo / "apps/web/AGENTES.md").write_text("alterado\n")
        pack = PACKS / "frontend"
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(pack / "scripts" / "verificar-nucleo.py"), "--docs", "apps/web/docs"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(PACKS / "backend" / "scripts" / "verificar-nucleo.py"), "--docs", "apps/api/docs"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)

    def test_codeowners_y_deny_conviven(self):
        self.instalar_ambos()
        co = (self.repo / ".github/CODEOWNERS").read_text()
        self.assertIn("/apps/api/docs/scripts/ @a", co)
        self.assertIn("/apps/web/docs/scripts/ @b", co)
        self.assertEqual(co.count("# >>> uxyngraphar núcleo"), 2)
        deny = (self.repo / ".claude/settings.json").read_text()
        self.assertIn("Edit(apps/api/AGENTES.md)", deny)
        self.assertIn("Edit(apps/web/AGENTES.md)", deny)

    def test_gancho_vigila_ambos_packs(self):
        self.instalar_ambos()
        for app in ("api", "web"):
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(self.repo / f"apps/{app}/docs/scripts/instalar-ganchos.py"), "--docs", f"apps/{app}/docs"], cwd=self.repo, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        gancho = (self.repo / ".git/hooks/pre-commit").read_text()
        self.assertIn('DOCS_LIST="apps/api/docs apps/web/docs"', gancho)
        self.assertEqual(gancho.count("for DOCS in"), 1)
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_nombre_de_carpeta_invalido(self):
        r = instalar_pack("servidor", self.repo, "documentacion")
        self.assertEqual(r.returncode, 2)
        self.assertIn("docs", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
