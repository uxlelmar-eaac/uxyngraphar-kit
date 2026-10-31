#!/usr/bin/env python3
"""Pruebas del validador de documentación (validar-documentacion.py)."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPTS = AQUI.parent
sys.path.insert(0, str(AQUI))

import validar_enlaces  # noqa: E402
import validar_estructura  # noqa: E402
from validar_comun import Opciones, Pack, Reporte, detectar_tipo, opciones_desde_entorno, resolver_docs, sin_codigo  # noqa: E402

_spec = importlib.util.spec_from_file_location("validar_documentacion", SCRIPTS / "validar-documentacion.py")
assert _spec and _spec.loader
validador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validador)

FICHA_MEJ = "---\nid: {id}\nstatus: {status}\ntipo: refactor\nseveridad: baja\nproposed_at: {fecha}\n{extra}---\n# {id}\n"


def crear_pack(raiz: Path, titulo: str = "servidor") -> Pack:
    docs = raiz / "docs"
    for d in validar_estructura.CARPETAS:
        (docs / d).mkdir(parents=True, exist_ok=True)
        (docs / d / "INDICE.md").write_text("# i\n", encoding="utf-8")
    for sec in validar_estructura.SECCIONES_ESTADO:
        for est in validar_estructura.ESTADOS:
            (docs / sec / est).mkdir(parents=True, exist_ok=True)
    for n in ("INDICE.md", "PROTOCOLO.md"):
        (docs / n).write_text("# x\n", encoding="utf-8")
    (docs / "00-nucleo" / "registro-ids-compartidos.md").write_text("# r\n", encoding="utf-8")
    (raiz / "AGENTES.md").write_text(f"# AGENTES.md — {titulo}\n", encoding="utf-8")
    return Pack(docs=docs.resolve(), cwd=raiz.resolve(), tipo=titulo)


def ficha(pack: Pack, sec: str, estado: str, nombre: str, texto: str, fecha: str = "2026-10-01") -> Path:
    p = pack.docs / sec / estado / fecha / f"{nombre}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8")
    return p


def mej(ident: str, status: str = "pending", extra: str = "", fecha: str = "2026-10-01") -> str:
    return FICHA_MEJ.format(id=ident, status=status, extra=extra, fecha=fecha)


def ejecutar(pack: Pack, **flags: object) -> Reporte:
    rep = Reporte(imprimir=False)
    validador.validar(pack, rep, Opciones(**flags))  # type: ignore[arg-type]
    return rep


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        self.pack = crear_pack(self.raiz)

    def assertAviso(self, rep: Reporte, texto: str) -> None:
        self.assertTrue(any(texto in m for m in rep.avisos), (texto, rep.avisos, rep.errores))

    def assertError(self, rep: Reporte, texto: str) -> None:
        self.assertTrue(any(texto in m for m in rep.errores), (texto, rep.errores))


class TestEstructura(Base):
    def test_pack_minimo_valido(self) -> None:
        rep = ejecutar(self.pack)
        self.assertEqual((rep.errores, rep.avisos), ([], []))

    def test_falta_indice_y_carpeta(self) -> None:
        (self.pack.docs / "PROTOCOLO.md").unlink()
        shutil.rmtree(self.pack.docs / "30-manuales")
        rep = ejecutar(self.pack)
        self.assertError(rep, "PROTOCOLO.md")
        self.assertError(rep, "30-manuales")

    def test_falta_agentes(self) -> None:
        (self.raiz / "AGENTES.md").unlink()
        self.assertError(ejecutar(self.pack), "AGENTES.md")

    def test_subcarpeta_y_ficha_sin_fecha(self) -> None:
        base = self.pack.docs / "45-mejoras-propuestas" / "01-pendientes"
        (base / "agosto").mkdir()
        (base / "suelta.md").write_text("# s\n", encoding="utf-8")
        rep = ejecutar(self.pack)
        self.assertAviso(rep, "YYYY-MM-DD")
        self.assertAviso(rep, "sin carpeta de fecha")

    def test_plantilla_sin_id(self) -> None:
        (self.pack.docs / "05-instrucciones" / "_PLANTILLA.md").write_text("sin frontmatter Contrato IA\n", encoding="utf-8")
        self.assertError(ejecutar(self.pack), "Sin id en frontmatter")

    def test_script_con_crlf(self) -> None:
        s = self.pack.docs / "scripts"
        s.mkdir()
        (s / "x.sh").write_bytes(b"#!/usr/bin/env bash\r\necho hola\r\n")
        self.assertError(ejecutar(self.pack), "CRLF")


class TestEnlacesYSecretos(Base):
    def test_enlace_roto_pero_no_en_codigo_ni_externo(self) -> None:
        (self.pack.docs / "10-guias" / "a.md").write_text(
            "[roto](nada.md) `[ej](nada2.md)`\n```\n[ej](nada3.md)\n```\n[web](https://x.y) [pack](../00-nucleo/INDICE.md) [fuera](../../../src/a.ts)\n",
            encoding="utf-8",
        )
        rotos = [d for _, d in validar_enlaces.enlaces_rotos(self.pack)]
        self.assertEqual(rotos, ["nada.md"])

    def test_secreto_real_vs_placeholder(self) -> None:
        (self.pack.docs / "10-guias" / "s.md").write_text(
            "api_key: abcdefghijklmnop1234\ntoken: <API_TOKEN_PLACEHOLDER>\nBearer abcdefghijklmnopqrstuvwxyz\nel token se guarda en el gestor de secretos\n",
            encoding="utf-8",
        )
        hallazgos = validar_enlaces.secretos_posibles(self.pack)
        self.assertEqual(len(hallazgos), 2)
        self.assertAviso(ejecutar(self.pack), "Posibles secretos")

    def test_sin_codigo(self) -> None:
        self.assertEqual(sin_codigo("a `[x](y)` b\n```\n[z](w)\n```\nc"), "a  b\n\nc")


class TestEnlacesARaizInstalada(unittest.TestCase):
    """Los enlaces del pack a AGENTES.md/AGENTS.md deben funcionar en el proyecto instalado,
    donde esos archivos van junto a `docs/` (clasificacion.destino) y no dentro."""

    def test_enlaces_a_archivos_de_raiz_resuelven_tras_instalar(self) -> None:
        sys.path.insert(0, str(SCRIPTS / "nucleo"))
        import clasificacion as cl  # noqa: E402

        pack = SCRIPTS.parent
        rotos = []
        for md in sorted(pack.rglob("*.md")):
            rel = md.relative_to(pack).as_posix()
            if "__pycache__" in rel or cl.clasificar(rel) not in ("N", "P", "M"):
                continue  # solo lo que se instala; el contenido del proyecto (C) no es del pack
            instalado = Path("/repo") / cl.destino(rel)
            for m in validar_enlaces.ENLACE_RE.finditer(sin_codigo(md.read_text(encoding="utf-8"))):
                ruta = m.group(1).split("#", 1)[0]
                nombre = ruta.rpartition("/")[2]
                if nombre not in cl.EN_RAIZ:
                    continue
                esperado = Path("/repo") / cl.destino(nombre)
                if Path(os.path.normpath(instalado.parent / ruta)) != esperado:
                    rotos.append(f"{rel}: {m.group(1)}")
        self.assertEqual(rotos, [])


class TestFichas(Base):
    def test_status_no_corresponde_a_carpeta(self) -> None:
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-a", mej("MEJ-1-a", "approved"))
        rep = ejecutar(self.pack)
        self.assertAviso(rep, "no corresponde a 01-pendientes")
        self.assertError(ejecutar(self.pack, estados=True), "no corresponde a 01-pendientes")

    def test_id_duplicado_y_nombre_distinto(self) -> None:
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-a", mej("MEJ-1-a"))
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-b", mej("MEJ-1-a"))
        rep = ejecutar(self.pack)
        self.assertAviso(rep, "id duplicado")
        self.assertAviso(rep, "Nombre de archivo ≠ id")
        self.assertError(ejecutar(self.pack, ids=True), "id duplicado")

    def test_enum_invalido_y_fecha_distinta(self) -> None:
        texto = mej("MEJ-1-a", fecha="2026-09-30").replace("tipo: refactor", "tipo: raro")
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-a", texto)
        rep = ejecutar(self.pack)
        self.assertAviso(rep, "tipo: «raro»")
        self.assertAviso(rep, "Carpeta de fecha")

    def test_sin_frontmatter_e_id(self) -> None:
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-a", "# sin yaml\n")
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-b", "---\nstatus: pending\n---\n# x\n")
        rep = ejecutar(self.pack)
        self.assertError(rep, "sin frontmatter")
        self.assertError(rep, "sin id")

    def test_placeholder_en_completada(self) -> None:
        ficha(self.pack, "46-evolucion-documentacion", "03-completadas", "EVO-1-a",
              "---\nid: EVO-1-a\nstatus: done\ntipo: proceso\nimpacto: ambos\nproposed_at: 2026-10-01\ninstruction_derivada: PENDIENTE-YYYYMMDD-NNN\n---\n# x\n")
        self.assertAviso(ejecutar(self.pack), "instruction_derivada sin completar")

    def test_vinculo_colgante(self) -> None:
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-a", mej("MEJ-1-a", extra="mejoras_propuestas: [MEJ-9-fantasma]\n"))
        self.assertAviso(ejecutar(self.pack), "MEJ-9-fantasma")
        self.assertError(ejecutar(self.pack, vinculos=True), "MEJ-9-fantasma")

    def test_vinculo_valido_no_avisa(self) -> None:
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-a", mej("MEJ-1-a", extra="mejoras_propuestas: [MEJ-1-b]\n"))
        ficha(self.pack, "45-mejoras-propuestas", "01-pendientes", "MEJ-1-b", mej("MEJ-1-b"))
        self.assertEqual(ejecutar(self.pack).avisos, [])

    def test_instruccion_done_sin_vinculos_y_presupuesto(self) -> None:
        texto = "---\nid: 20261001-001-x\nstatus: done\nacto: crear\nvinculos_salida: []\npresupuesto_max_docs: 1\nlectura_minima: [a, b]\nespejo_leer: [c]\ncreated: 2026-10-01T00:00:00Z\n---\n# x\n"
        ficha(self.pack, "05-instrucciones", "03-completadas", "x", texto)
        self.assertEqual(ejecutar(self.pack).errores, [])
        rep = ejecutar(self.pack, vinculos=True, presupuesto=True)
        self.assertError(rep, "sin vinculos_salida")
        self.assertError(rep, "Presupuesto docs excedido")

    def test_r21_alcance_de_codigo(self) -> None:
        base = "---\nid: 20261001-00{n}-{s}\nstatus: {st}\nacto: crear\ncreated: 2026-10-01T00:00:00Z\nanclas_codigo: [a, b, c, d, e, f, g]\npresupuesto_max_archivos_codigo: 7\n{extra}---\n# x\n"
        ficha(self.pack, "05-instrucciones", "01-pendientes", "sin", base.format(n=1, s="sin", st="awaiting_approval", extra=""))
        just = 'ampliacion_justificacion: "Contrato compartido: a medias rompe la compilación entre entregas."\n'
        ficha(self.pack, "05-instrucciones", "02-en-progreso", "amp", base.format(n=2, s="amp", st="approved", extra="ampliacion_factor: 1.5\n" + just))
        ficha(self.pack, "05-instrucciones", "03-completadas", "old", base.format(n=3, s="old", st="done", extra=""))
        rep = ejecutar(self.pack)
        self.assertError(rep, "R-21 7 archivos de código > estándar 5")
        self.assertError(rep, "R-21 ampliación de alcance sin aprobación humana")
        self.assertAviso(rep, "old.md")   # histórico: solo aviso
        self.assertFalse(any("old.md" in m for m in rep.errores))


class TestPack(Base):
    def test_cliente_enlaza_servidor(self) -> None:
        pack = crear_pack(Path(tempfile.mkdtemp()), "cliente")
        self.addCleanup(shutil.rmtree, pack.cwd, True)
        (pack.docs / "10-guias" / "g.md").write_text("ver ../../servidor/AGENTES.md y igual que el servidor\n", encoding="utf-8")
        rep = ejecutar(pack)
        self.assertAviso(rep, "autocontenido")
        self.assertError(ejecutar(pack, cliente=True), "../../servidor/")

    def test_servidor_no_aplica_regla_cliente(self) -> None:
        (self.pack.docs / "10-guias" / "g.md").write_text("ver ../../servidor/AGENTES.md\n", encoding="utf-8")
        self.assertFalse(any("servidor" in m for m in ejecutar(self.pack, cliente=True).errores))

    def test_decisiones_antiguas(self) -> None:
        shutil.copytree(SCRIPTS / "decisiones", self.pack.docs / "scripts" / "decisiones", ignore=shutil.ignore_patterns("__pycache__", "test_*"))
        ficha(self.pack, "46-evolucion-documentacion", "01-pendientes", "EVO-1-a",
              "---\nid: EVO-1-a\nstatus: pending\ntipo: proceso\nimpacto: ambos\nproposed_at: 2020-01-01\n---\n# x\n", fecha="2020-01-01")
        self.assertAviso(ejecutar(self.pack), "con más de 30 días")
        self.assertError(ejecutar(self.pack, decisiones=True), "con más de 30 días")
        self.assertEqual([m for m in ejecutar(self.pack, max_dias_decisiones=100000).avisos if "30" in m], [])


class TestConfiguracion(unittest.TestCase):
    def test_strict_all_activa_todo(self) -> None:
        op = opciones_desde_entorno({"STRICT_ALL": "1"})
        self.assertTrue(all([op.decisiones, op.vinculos, op.presupuesto, op.cliente, op.estados, op.ids]))

    def test_flags_individuales_y_dias(self) -> None:
        op = opciones_desde_entorno({"STRICT_IDS": "1", "DECISIONES_MAX_DAYS": "7"})
        self.assertTrue(op.ids)
        self.assertFalse(op.estados)
        self.assertEqual(op.max_dias_decisiones, 7)
        self.assertEqual(opciones_desde_entorno({"DECISIONES_MAX_DAYS": "x"}).max_dias_decisiones, 30)

    def test_resolver_docs_y_tipo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            self.assertEqual(resolver_docs({}, raiz), raiz / "docs")
            self.assertEqual(resolver_docs({"DOCS_DIR": "otra"}, raiz), raiz / "otra")
            (raiz / "INDICE.md").write_text("x", encoding="utf-8")
            self.assertEqual(resolver_docs({}, raiz), raiz)
            (raiz / "AGENTES.md").write_text("# AGENTES.md — cliente\n", encoding="utf-8")
            self.assertEqual(detectar_tipo(raiz, raiz), "cliente")

    def test_ejecucion_completa_por_linea_de_comandos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = crear_pack(Path(tmp))
            exe = [sys.executable, "-X", "utf8", "-I", str(SCRIPTS / "validar-documentacion.py")]
            ok = subprocess.run(exe, cwd=pack.cwd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(ok.returncode, 0, ok.stderr)
            (pack.docs / "INDICE.md").unlink()
            mal = subprocess.run(exe, cwd=pack.cwd, capture_output=True, text=True, encoding="utf-8", env={**os.environ, "DOCS_DIR": "docs"})
            self.assertEqual(mal.returncode, 1)
            self.assertIn("FALLÓ", mal.stdout)


if __name__ == "__main__":
    unittest.main()
