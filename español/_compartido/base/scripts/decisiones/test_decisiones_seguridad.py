#!/usr/bin/env python3
"""Regresión — integridad del frontmatter, rutas seguras y validación de acciones.

Cubre los hallazgos de la auditoría 2026-10: C1 (YAML sin salto final tras aplicar),
C2 (escritura fuera de las raíces vía sesion-activa.json), A2 (acciones inválidas),
A3 (acciones de auditoría) y B1/B2 (comentarios YAML y destino de estado).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from applier import apply_session
from common import (
    DEFAULT_OPTIONS,
    estado_dest_rel,
    parse_simple_yaml,
    rebuild_content,
    split_frontmatter,
    update_frontmatter_raw,
)
from scanner import scan_all
from session import register_decision
from session_acciones import error_de_accion

CLI = Path(__file__).resolve().parent / "decisiones.py"

# tipo -> (carpeta pendiente, status pendiente)
FICHAS = {
    "instruccion": ("05-instrucciones/01-pendientes/2026-01-01", "awaiting_approval"),
    "herramienta": ("35-herramientas/propuestas/01-pendientes/2026-01-01", "pending"),
    "mejora": ("45-mejoras-propuestas/01-pendientes/2026-01-01", "pending"),
    "adr": ("20-decisiones/01-pendientes/2026-01-01", "propuesta"),
    "auditoria": ("40-auditorias/01-pendientes/2026-01-01", "active"),
    "evolucion": ("46-evolucion-documentacion/01-pendientes/2026-01-01", "pending"),
}


def escribir_ficha(root: Path, tipo: str, newline: str = "\n") -> Path:
    carpeta, status = FICHAS[tipo]
    p = root / carpeta / f"{tipo}-x.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    texto = f"---\nid: {tipo}-x\nstatus: {status}\nproposed_at: 2026-01-01\n---\n# Ficha {tipo}\n\nContexto.\n"
    p.write_bytes(texto.replace("\n", newline).encode("utf-8"))
    return p


def sesion(item, action: str) -> dict:
    entry = {"id": item.id, "group_id": item.id, "action": action, "applied": False}
    entry.update({k: item.to_dict()[k] for k in ("path", "docs_root", "tipo")})
    entry["opciones"] = [o.action for o in item.options]
    return {"session_id": "t", "decisions": [entry]}


class TestFrontmatterIntegro(unittest.TestCase):
    def _ciclo(self, newline: str) -> None:
        for tipo, opciones in DEFAULT_OPTIONS.items():
            for action, _ in opciones:
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp).resolve()
                    escribir_ficha(root, tipo, newline)
                    (item,) = scan_all([(root, "t")])
                    res = apply_session(sesion(item, action), permitidas=[root])
                    self.assertTrue(res[0]["ok"], (tipo, action, res))
                    md = next(p for p in root.rglob("*.md") if p.name == f"{tipo}-x.md")
                    fm, _, bruto = split_frontmatter(md.read_text(encoding="utf-8"))
                    self.assertIsNotNone(bruto, f"frontmatter roto: {tipo}/{action}")
                    self.assertEqual(fm["id"], f"{tipo}-x")
                    self.assertNotRegex(bruto, r"[^\n]---\s*\n$", f"cierre pegado: {tipo}/{action}")
                    self.assertEqual([i for i in scan_all([(root, "t")]) if i.id == item.id and action != "posponer"], [])

    def test_ciclo_aplicar_y_reescanear_lf(self) -> None:
        self._ciclo("\n")

    def test_ciclo_aplicar_y_reescanear_crlf(self) -> None:
        self._ciclo("\r\n")

    def test_update_siempre_termina_en_salto(self) -> None:
        self.assertTrue(update_frontmatter_raw("id: a\nstatus: x", {"status": "y"}).endswith("\n"))
        self.assertTrue(update_frontmatter_raw("id: a", {"nuevo": "1"}).endswith("\n"))
        self.assertIn("status: y\n---\n", rebuild_content("id: a\nstatus: y", "cuerpo"))

    def test_auditoria_aprobar_cierra_y_mueve(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            escribir_ficha(root, "auditoria")
            (item,) = scan_all([(root, "t")])
            apply_session(sesion(item, "aprobar"), permitidas=[root])
            destino = root / "40-auditorias/03-completadas/2026-01-01/auditoria-x.md"
            self.assertTrue(destino.exists())
            self.assertEqual(split_frontmatter(destino.read_text(encoding="utf-8"))[0]["status"], "cerrada")


class TestComentariosYDestino(unittest.TestCase):
    def test_parse_descarta_comentario_inline(self) -> None:
        self.assertEqual(parse_simple_yaml("status: pending  # nota\n")["status"], "pending")

    def test_parse_conserva_almohadilla_entre_comillas(self) -> None:
        self.assertEqual(parse_simple_yaml('title: "a # b"\n')["title"], "a # b")

    def test_update_no_trunca_valor_con_comillas(self) -> None:
        out = update_frontmatter_raw('title: "a # b"\nstatus: x # c', {"status": "y"})
        self.assertIn('title: "a # b"', out)
        self.assertIn("status: y # c", out)

    def test_destino_archivo_directo_bajo_estado(self) -> None:
        rel = estado_dest_rel("45-mejoras-propuestas/01-pendientes/x.md", {"proposed_at": "2026-02-03"}, "02-en-progreso")
        self.assertEqual(rel, "45-mejoras-propuestas/02-en-progreso/2026-02-03/x.md")

    def test_destino_conserva_carpeta_de_fecha(self) -> None:
        rel = estado_dest_rel("45/01-pendientes/2026-01-01/x.md", {}, "05-canceladas")
        self.assertEqual(rel, "45/05-canceladas/2026-01-01/x.md")


class TestEscrituraAtomica(unittest.TestCase):
    def test_save_json_no_deja_temporales(self) -> None:
        from common import load_json, save_json

        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "sub" / "sesion.json"
            save_json(destino, {"a": 1})
            save_json(destino, {"a": 2, "ñ": "ü"})
            self.assertEqual(load_json(destino), {"a": 2, "ñ": "ü"})
            self.assertEqual([p.name for p in destino.parent.iterdir()], ["sesion.json"])


class TestRutasSeguras(unittest.TestCase):
    def _intento(self, docs_root: str, path: str, root: Path) -> list:
        entry = {"id": "x", "action": "aprobar", "tipo": "mejora", "docs_root": docs_root, "path": path, "applied": False}
        return apply_session({"session_id": "t", "decisions": [entry]}, permitidas=[root.resolve()])

    def test_rechaza_traversal_ruta_absoluta_y_raiz_ajena(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as fuera:
            root = Path(tmp)
            victima = Path(fuera) / "v.md"
            victima.write_text("---\nid: v\nstatus: pending\n---\n# V\n", encoding="utf-8")
            antes = victima.read_text(encoding="utf-8")
            casos = [
                (str(root), os.path.relpath(victima, root)),
                (str(root), str(victima)),
                (str(root), "..\\fuera\\v.md"),
                (fuera, "v.md"),
                ("", "v.md"),
            ]
            for docs_root, path in casos:
                res = self._intento(docs_root, path, root)
                self.assertFalse(res[0]["ok"], (docs_root, path))
                self.assertIn("rechazada", res[0]["error"])
            self.assertEqual(victima.read_text(encoding="utf-8"), antes)

    @unittest.skipIf(os.name == "nt", "enlaces simbólicos requieren privilegios en Windows")
    def test_rechaza_enlace_simbolico_que_escapa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as fuera:
            root = Path(tmp)
            (Path(fuera) / "v.md").write_text("---\nid: v\nstatus: pending\n---\n# V\n", encoding="utf-8")
            (root / "enlace").symlink_to(fuera, target_is_directory=True)
            res = self._intento(str(root), "enlace/v.md", root)
            self.assertFalse(res[0]["ok"])


class TestAccionesValidas(unittest.TestCase):
    def test_register_rechaza_errata(self) -> None:
        item = {"tipo": "mejora", "options": [{"action": "aprobar"}]}
        with self.assertRaises(ValueError):
            register_decision("x", "aprovar", item)

    def test_accion_ajena_al_tipo(self) -> None:
        self.assertIsNotNone(error_de_accion("instruccion", "promover"))
        self.assertIsNone(error_de_accion("instruccion", "aprobar"))
        self.assertIsNone(error_de_accion("mejora", "posponer"))

    def test_apply_no_marca_aplicada_una_accion_invalida(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            p = escribir_ficha(root, "mejora")
            antes = p.read_bytes()
            (item,) = scan_all([(root, "t")])
            ses = sesion(item, "aprovar")
            res = apply_session(ses, permitidas=[root])
            self.assertFalse(res[0]["ok"])
            self.assertFalse(ses["decisions"][0]["applied"])
            self.assertEqual(p.read_bytes(), antes)


class TestMultiPack(unittest.TestCase):
    """Mismo id en dos packs: las decisiones no se pisan y register exige --pack."""

    def _cli(self, dirs: str, *args: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "DOCS_DIRS": dirs}
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(CLI), *args], capture_output=True, text=True, env=env, encoding="utf-8")

    def test_mismo_id_en_dos_packs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp, "backend"), Path(tmp, "frontend")
            for r in (a, b):
                (r / "PROTOCOLO.md").parent.mkdir(parents=True, exist_ok=True)
                (r / "PROTOCOLO.md").write_text("x", encoding="utf-8")
                escribir_ficha(r, "mejora")
            dirs = f"{a},{b}"
            amb = self._cli(dirs, "register", "--id", "mejora-x", "--action", "aprobar")
            self.assertEqual(amb.returncode, 2)
            self.assertIn("--pack", amb.stderr)
            self.assertEqual(self._cli(dirs, "register", "--id", "mejora-x", "--pack", "backend", "--action", "aprobar").returncode, 0)
            self.assertEqual(self._cli(dirs, "register", "--id", "mejora-x", "--pack", "frontend", "--action", "rechazar").returncode, 0)
            self.assertEqual(self._cli(dirs, "apply").returncode, 0)
            self.assertTrue((a / "45-mejoras-propuestas/02-en-progreso/2026-01-01/mejora-x.md").exists())
            self.assertTrue((b / "45-mejoras-propuestas/05-canceladas/2026-01-01/mejora-x.md").exists())


class TestCLI(unittest.TestCase):
    def _cli(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "DOCS_DIRS": str(root)}
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(CLI), *args], capture_output=True, text=True, env=env, encoding="utf-8")

    def test_register_id_inexistente_falla_con_codigo_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            r = self._cli(Path(tmp), "register", "--id", "no-existe", "--action", "aprobar")
            self.assertEqual(r.returncode, 2)

    def test_register_errata_falla_con_codigo_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            escribir_ficha(root, "mejora")
            r = self._cli(root, "register", "--id", "mejora-x", "--action", "aprovar")
            self.assertEqual(r.returncode, 2)
            self.assertIn("no válida", r.stderr)

    def test_flujo_completo_por_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            escribir_ficha(root, "mejora")
            self.assertEqual(self._cli(root, "register", "--id", "mejora-x", "--action", "aprobar").returncode, 0)
            self.assertEqual(self._cli(root, "apply").returncode, 0)
            self.assertIn("Sin decisiones pendientes", self._cli(root, "scan").stdout)


if __name__ == "__main__":
    unittest.main()
