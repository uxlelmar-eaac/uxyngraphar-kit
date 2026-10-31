#!/usr/bin/env python3
"""Pruebas de las reglas del proyecto (96-reglas-proyecto/): clasificación, validación e índice, contexto filtrado por anclas,
control de la puerta (bloquea, avisa, excepción aprobada y sin aprobar, cambios de reglas), cierre y configuración."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPTS = AQUI.parent
for sub in ("", "nucleo", "control", "tokens", "decisiones"):
    sys.path.insert(0, str(AQUI.parent / sub) if sub else str(AQUI))

import clasificacion as cl  # noqa: E402
import reglas_control  # noqa: E402
import reglas_proyecto as rp  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402
from paquete import construir  # noqa: E402

CARPETA_PACK = SCRIPTS.parent / rp.CARPETA
REGLA = """---
id: {id}
titulo: Sin console.log
status: {status}
nivel: {nivel}
aplica_a:
  - src/**/*.ts
resumen: {resumen}
comprobacion_prohibido: "console\\.log"
---
# {id}

**Regla:** usa el logger.
"""
INSTRUCCION = """---
id: {id}
status: {status}
source: human
areas: [x]
acto: crear
lectura_minima: []
anclas_codigo:
{anclas}
espejo_actualizar: []
{extra}---
# {id}

## Objetivo

Prueba.
"""


def lista(items: list[str]) -> str:
    return "".join(f"  - {x}\n" for x in items)


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name)
        self.docs = self.repo / "docs"
        (self.docs / rp.CARPETA).mkdir(parents=True)
        for f in CARPETA_PACK.iterdir():
            (self.docs / rp.CARPETA / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
        (self.repo / "src").mkdir()
        self.cfg = cfgmod.por_defecto()
        self.cfg["codigo"]["extensiones"] = [".ts"]

    def regla(self, ident: str = "RP-001", status: str = "activa", nivel: str = "bloqueante", resumen: str = "Nada de console.log en src") -> Path:
        f = self.docs / rp.CARPETA / f"{ident}.md"
        f.write_text(REGLA.format(id=ident, status=status, nivel=nivel, resumen=resumen), encoding="utf-8")
        return f

    def instruccion(self, ident: str, status: str, anclas: list[str], excepciones: list[str] | None = None, carpeta: str = "02-en-progreso") -> str:
        extra = f"excepciones_reglas:\n{lista(excepciones)}" if excepciones else ""
        rel = f"docs/05-instrucciones/{carpeta}/2026-10-30/{ident}.md"
        f = self.repo / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(INSTRUCCION.format(id=ident, status=status, anclas=lista(anclas), extra=extra), encoding="utf-8")
        return rel

    def codigo(self, rel: str, texto: str) -> str:
        (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.repo / rel).write_text(texto, encoding="utf-8")
        return rel

    def control(self, cambiados: list[str]) -> list[tuple[str, str]]:
        return reglas_control.evaluar(self.repo, cambiados, self.cfg, "docs", lambda r: r.startswith("src/") and r.endswith(".ts"))


class TestReglas(Base):
    def test_clasificacion(self) -> None:
        self.assertEqual(cl.clasificar("96-reglas-proyecto/RP-001.md"), "C")
        self.assertEqual(cl.clasificar("96-reglas-proyecto/EX-20261030-x.md"), "C")
        self.assertEqual(cl.clasificar("96-reglas-proyecto/_PROTOCOLO.md"), "N")
        self.assertEqual(cl.clasificar("96-reglas-proyecto/_PLANTILLA-regla.md"), "N")
        self.assertEqual(cl.clasificar("96-reglas-proyecto/INDICE.md"), "M")

    def test_el_esqueleto_llega_sin_reglas(self) -> None:
        self.assertEqual(sorted(p.name for p in CARPETA_PACK.glob("RP-*.md")), [])
        self.assertEqual(rp.todas(self.docs), [])
        self.assertTrue(rp.indice_al_dia(self.docs))

    def test_validacion_e_indice(self) -> None:
        self.regla()
        mala = self.docs / rp.CARPETA / "RP-002.md"
        mala.write_text("---\nid: RP-9\nstatus: viva\nnivel: alto\n---\n", encoding="utf-8")
        reglas = {r.ruta.name: r for r in rp.todas(self.docs)}
        self.assertEqual(reglas["RP-001.md"].problemas, [])
        self.assertTrue(len(reglas["RP-002.md"].problemas) >= 3)
        self.assertFalse(rp.indice_al_dia(self.docs))
        self.assertTrue(rp.regenerar_indice(self.docs))
        indice = (self.docs / rp.CARPETA / "INDICE.md").read_text(encoding="utf-8")
        self.assertIn("| RP-001 | bloqueante | `src/**/*.ts` | Nada de console.log en src |", indice)
        self.assertNotIn("RP-002", indice)
        self.assertTrue(rp.indice_al_dia(self.docs))
        self.assertFalse(rp.regenerar_indice(self.docs))

    def test_contexto_solo_trae_las_reglas_de_las_anclas(self) -> None:
        self.regla()
        self.regla("RP-002", nivel="aviso", resumen="Nombres en inglés")
        (self.docs / rp.CARPETA / "RP-003.md").write_text(REGLA.format(id="RP-003", status="activa", nivel="bloqueante", resumen="Otra")
                                                          .replace("src/**/*.ts", "api/**/*.py"), encoding="utf-8")
        self.regla("RP-004", status="retirada", resumen="Retirada")
        rel = self.instruccion("20261030-001-x", "approved", ["src/a.ts:1-10"])
        paq = construir(self.docs, self.repo / rel, repo=self.repo)
        bloque = next(p for p in paq.partes if p.titulo.startswith("REGLAS DEL PROYECTO"))
        self.assertIn("RP-001 [bloqueante] Nada de console.log en src", bloque.texto)
        self.assertIn("usa el logger", bloque.texto)                 # cuerpo de la bloqueante
        self.assertIn("RP-002 [aviso] Nombres en inglés", bloque.texto)
        self.assertNotIn("**Regla:** usa el logger.\n  RP-002", bloque.texto)
        self.assertEqual(bloque.texto.count("usa el logger"), 1)      # el cuerpo de la de aviso no viaja
        self.assertNotIn("RP-003", bloque.texto)
        self.assertNotIn("RP-004", bloque.texto)
        sin = construir(self.docs, self.repo / self.instruccion("20261030-002-y", "approved", ["lib/z.go"]), repo=self.repo)
        self.assertFalse(any(p.titulo.startswith("REGLAS DEL PROYECTO") for p in sin.partes))

    def test_control_bloquea_y_avisa(self) -> None:
        self.regla()
        self.regla("RP-002", nivel="aviso", resumen="Aviso")
        mal = self.codigo("src/a.ts", "const x = 1;\nconsole.log(x);\n")
        bien = self.codigo("src/b.ts", "logger.info(1);\n")
        h = self.control([mal, bien])
        self.assertEqual([n for n, m in h if "RP-001" in m], ["bloqueante"])
        self.assertEqual([n for n, m in h if "RP-002" in m], ["aviso"])
        self.assertIn("línea 2", next(m for n, m in h if "RP-001" in m))
        self.cfg["niveles"]["reglas_proyecto"] = "apagado"
        self.assertEqual(self.control([mal]), [])

    def test_obligatorio(self) -> None:
        f = self.regla()
        f.write_text(f.read_text(encoding="utf-8").replace('comprobacion_prohibido: "console\\.log"', 'comprobacion_obligatorio: "^// SPDX"'), encoding="utf-8")
        self.assertTrue(self.control([self.codigo("src/a.ts", "x\n")]))
        self.assertEqual(self.control([self.codigo("src/b.ts", "// SPDX-License: MIT\nx\n")]), [])

    def test_excepcion_aprobada_y_sin_aprobar(self) -> None:
        self.regla()
        mal = self.codigo("src/a.ts", "console.log(1);\n")
        aprobada = self.instruccion("20261030-001-x", "approved", ["src/a.ts"], ['"RP-001: depuración temporal"'])
        self.assertEqual(self.control([mal, aprobada]), [])
        pendiente = self.instruccion("20261030-002-y", "awaiting_approval", ["src/a.ts"], ['"RP-001: porque sí"'], "01-pendientes")
        h = self.control([mal, pendiente])
        self.assertTrue(any("sin estar aprobada" in m for _n, m in h))
        self.assertTrue(any("incumple RP-001" in m for _n, m in h))
        mala = self.instruccion("20261030-003-z", "approved", ["src/a.ts"], ['"sin formato"'])
        self.assertTrue(any("use «RP-NNN: motivo»" in m for _n, m in self.control([mala])))

    def test_modos_de_excepcion(self) -> None:
        self.regla()
        mal = self.codigo("src/a.ts", "console.log(1);\n")
        ins = self.instruccion("20261030-001-x", "approved", ["src/a.ts"], ['"RP-001: motivo"'])
        self.cfg["reglas_proyecto"]["excepciones"] = "prohibidas"
        h = self.control([mal, ins])
        self.assertTrue(any("las prohíbe" in m for _n, m in h) and any("incumple RP-001" in m for _n, m in h))
        self.cfg["reglas_proyecto"]["excepciones"] = "ficha_aparte"
        self.assertTrue(any("incumple RP-001" in m for _n, m in self.control([mal, ins])))
        (self.docs / rp.CARPETA / "EX-20261030-x.md").write_text("---\nid: EX-20261030-x\nregla: RP-001\ninstruccion: 20261030-001-x\nstatus: aprobada\n---\n", encoding="utf-8")
        self.assertEqual(self.control([mal, ins]), [])

    def test_cambiar_reglas_exige_instruccion_aprobada(self) -> None:
        regla = f"docs/{rp.CARPETA}/RP-001.md"
        self.regla()
        self.assertTrue(any("sin una instrucción aprobada" in m for _n, m in self.control([regla])))
        pendiente = self.instruccion("20261030-001-x", "awaiting_approval", [regla], carpeta="01-pendientes")
        self.assertTrue(any("sin una instrucción aprobada" in m for _n, m in self.control([regla, pendiente])))
        aprobada = self.instruccion("20261030-002-y", "approved", [regla])
        self.assertEqual(self.control([regla, aprobada]), [])
        carpeta = self.instruccion("20261030-003-z", "approved", [f"docs/{rp.CARPETA}/"])
        self.assertEqual(self.control([regla, carpeta]), [])
        self.assertEqual(self.control([f"docs/{rp.CARPETA}/INDICE.md"]), [])   # derivado: lo vigila el doctor
        self.cfg["reglas_proyecto"]["cambios_reglas"] = "solo_humano"
        self.assertEqual(self.control([regla]), [])

    def test_cerrar_regenera_el_indice(self) -> None:
        import cerrar
        self.regla()
        rel = self.instruccion("20261030-001-x", "approved", [f"docs/{rp.CARPETA}/RP-001.md"])
        (self.repo / rel).write_text((self.repo / rel).read_text(encoding="utf-8").replace("espejo_actualizar: []", "espejo_actualizar: []\nvinculos_salida: [x]"), encoding="utf-8")
        salida = cerrar.cerrar(self.docs, "20261030-001-x")
        self.assertIn("96-reglas-proyecto/INDICE.md regenerado", salida)
        self.assertTrue(rp.indice_al_dia(self.docs))

    def test_configuracion(self) -> None:
        cfg = cfgmod.por_defecto()
        self.assertEqual(cfg["reglas_proyecto"], {"excepciones": "en_instruccion", "cambios_reglas": "instruccion_aprobada"})
        self.assertEqual(cfg["niveles"]["reglas_proyecto"], "bloqueante")
        self.assertEqual(cfgmod.validar(cfg), [])
        cfg["reglas_proyecto"] = {"excepciones": "siempre", "cambios_reglas": "agente"}
        errores = cfgmod.validar(cfg)
        self.assertTrue(any("excepciones" in e for e in errores) and any("cambios_reglas" in e for e in errores))
        (self.docs / "uxyngraphar.config.json").write_text(json.dumps({"reglas_proyecto": {"cambios_reglas": "solo_humano"}}), encoding="utf-8")
        efectiva, problemas = cfgmod.cargar(self.repo)
        self.assertEqual(problemas, [])
        self.assertEqual(efectiva["reglas_proyecto"]["excepciones"], "en_instruccion")   # lo no indicado conserva el valor por defecto

    def test_solo_humano_anade_reglas_deny(self) -> None:
        import proteccion
        self.assertEqual(proteccion.rutas_reglas_solo_humano(self.repo, "docs"), [])
        (self.docs / "uxyngraphar.config.json").write_text(json.dumps({"reglas_proyecto": {"cambios_reglas": "solo_humano"}}), encoding="utf-8")
        self.assertEqual(proteccion.rutas_reglas_solo_humano(self.repo, "docs"), [f"docs/{rp.CARPETA}/**"])

    def test_la_puerta_incluye_el_control(self) -> None:
        import puerta
        self.regla()
        mal = self.codigo("src/a.ts", "console.log(1);\n")
        h = puerta.evaluar(self.repo, [mal], {mal: ["console.log(1);"]}, self.cfg, "docs")
        self.assertTrue(any(x.control == "reglas_proyecto" and x.nivel == "bloqueante" for x in h))

    def test_doctor(self) -> None:
        import doctor
        self.assertEqual(doctor.reglas_proyecto(self.repo, "docs")[0].nivel, "OK")
        self.regla()
        c = doctor.reglas_proyecto(self.repo, "docs")[0]
        self.assertEqual(c.nivel, "ERROR")
        self.assertIn("INDICE.md no cuadra", c.mensaje)
        rp.regenerar_indice(self.docs)
        self.assertEqual(doctor.reglas_proyecto(self.repo, "docs")[0].nivel, "OK")
        (self.docs / rp.CARPETA / "RP-002.md").write_text("---\nid: RP-002\nstatus: activa\n---\n", encoding="utf-8")
        self.assertIn("inválida", doctor.reglas_proyecto(self.repo, "docs")[0].mensaje)

    def test_cli(self) -> None:
        self.regla()
        cli = [sys.executable, str(SCRIPTS / "reglas.py"), "--repo", str(self.repo)]
        self.assertEqual(subprocess.run([*cli, "validar"], capture_output=True).returncode, 1)   # índice desfasado
        self.assertEqual(subprocess.run([*cli, "indice"], capture_output=True).returncode, 0)
        r = subprocess.run([*cli, "validar"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("RP-001", subprocess.run([*cli, "listar"], capture_output=True, text=True).stdout)


if __name__ == "__main__":
    unittest.main()
