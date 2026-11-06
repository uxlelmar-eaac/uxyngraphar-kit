"""Pruebas de los paquetes que recuperan piezas del 1.x sin paquete propio: reglas-del-proyecto (96+97),
evolucion-del-sistema (46), revision-humana, contratos-entre-repos, arquitectura-por-capas y verificaciones-vivas (55)."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import repo
from test_pilotos import BaseApp, correr


def campo(ruta: Path, clave: str, valor: str) -> None:
    texto = ruta.read_text(encoding="utf-8")
    texto, n = re.subn(rf"^{clave}:.*$", f"{clave}: {valor}", texto, count=1, flags=re.M)
    if not n:
        texto = texto.replace("\n---", f"\n{clave}: {valor}\n---", 1)
    ruta.write_text(texto, encoding="utf-8")


class Base(BaseApp):
    def trabajo(self, pid: str, app: Path | None = None) -> Path:
        return (app or self.app) / "uxyngraphar" / "trabajo" / pid

    def nueva(self, pid: str, tipo: str, slug: str, app: Path | None = None) -> Path:
        app = app or self.app
        fichas = app / "uxyngraphar" / "paquetes" / pid / "scripts" / "comun" / "fichas.py"
        r = correr(fichas, "nueva", tipo, "--slug", slug, "--titulo", slug, cwd=app)
        self.assertEqual(r.returncode, 0, r.stderr)
        (ruta,) = self.trabajo(pid, app).rglob(f"*{slug}.md")
        return ruta

    def estado(self, pid: str, ruta: Path, nuevo: str, humano: bool = True, app: Path | None = None):
        app = app or self.app
        fichas = app / "uxyngraphar" / "paquetes" / pid / "scripts" / "comun" / "fichas.py"
        return correr(fichas, "estado", ruta.stem, nuevo, *(["--humano"] if humano else []), cwd=app)

    def ajustes(self, pid: str, valores: dict) -> None:
        (self.trabajo(pid) / "ajustes.json").write_text(json.dumps(valores), encoding="utf-8")

    def escribir(self, rel: str, texto: str) -> None:
        p = self.app / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")


class TestReglas(Base):
    PAQUETES = ["reglas-del-proyecto", "instrucciones-aprobadas"]

    def test_regla_excepcion_y_persona(self):
        regla = self.nueva("reglas-del-proyecto", "regla", "sin-console")
        campo(regla, "comprobacion_prohibido", r'"console\.log"')
        r = self.estado("reglas-del-proyecto", regla, "activa", humano=False)
        self.assertNotEqual(r.returncode, 0)
        r = correr(self.s("reglas-del-proyecto", "fichas.py"), "estado", regla.stem, "activa", "--humano", cwd=self.app, persona=False)
        self.assertIn("solo una persona", r.stderr)
        self.assertEqual(self.estado("reglas-del-proyecto", regla, "activa").returncode, 0)
        self.escribir("src/a.ts", "console.log('x');\n")
        r = correr(self.s("reglas-del-proyecto", "reglas.py"), "comprobar", cwd=self.app)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("src/a.ts", r.stdout)
        self.assertIn(regla.stem, correr(self.s("reglas-del-proyecto", "reglas.py"), "para", "src/a.ts:1-3", cwd=self.app).stdout)
        self.assertEqual(correr(self.s("reglas-del-proyecto", "verificar-reglas.py"), cwd=self.app).returncode, 1)
        excepcion = self.nueva("reglas-del-proyecto", "excepcion", "log-de-arranque")
        campo(excepcion, "regla", regla.stem)
        campo(excepcion, "archivos", "[src/a.ts]")
        campo(excepcion, "aprobada_por", "ana")
        self.assertEqual(self.estado("reglas-del-proyecto", excepcion, "aprobada").returncode, 0)
        r = correr(self.s("reglas-del-proyecto", "verificar-reglas.py"), cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_ajuste_local_con_huella(self):
        ajuste = self.nueva("reglas-del-proyecto", "ajuste", "paso-extra")
        campo(ajuste, "paquete", "instrucciones-aprobadas")
        reglas = self.s("reglas-del-proyecto", "reglas.py")
        self.assertIn("0 ajustes locales activos", correr(reglas, "ajustes", "instrucciones-aprobadas", cwd=self.app).stdout)
        self.assertNotEqual(correr(reglas, "aprobar-ajuste", ajuste.stem, cwd=self.app).returncode, 0)
        r = correr(reglas, "aprobar-ajuste", ajuste.stem, "--humano", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 ajustes locales activos", correr(reglas, "ajustes", "instrucciones-aprobadas", cwd=self.app).stdout)
        (activo,) = self.trabajo("reglas-del-proyecto").rglob(f"{ajuste.stem}.md")
        self.assertRegex(activo.read_text(encoding="utf-8"), r"huella: [0-9a-f]{64}")


class TestEvolucion(Base):
    PAQUETES = ["evolucion-del-sistema"]

    def test_matriz_y_exportacion_anonima(self):
        evo = self.nueva("evolucion-del-sistema", "evo", "falta-cobertura")
        s = self.s("evolucion-del-sistema", "evolucion.py")
        self.assertEqual(correr(s, "matriz", cwd=self.app).returncode, 0)
        self.assertTrue((self.trabajo("evolucion-del-sistema") / "MATRIZ-COBERTURA.md").is_file())
        listado = correr(self.s("evolucion-del-sistema", "fichas.py"), "listar", cwd=self.app).stdout
        self.assertIn(evo.stem, listado)
        self.assertNotIn("MATRIZ", listado)
        self.assertNotEqual(correr(s, "exportar", cwd=self.app).returncode, 0)
        self.assertEqual(self.estado("evolucion-del-sistema", evo, "approved").returncode, 0)
        r = correr(s, "exportar", "--humano", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        (exportacion,) = (self.trabajo("evolucion-del-sistema") / "exportaciones").glob("EXPORTACION-*.md")
        texto = exportacion.read_text(encoding="utf-8")
        self.assertIn(evo.stem, texto)
        self.assertNotIn(str(self.app), texto)


class TestRevisionHumana(Base):
    PAQUETES = ["revision-humana", "decisiones-de-arquitectura"]

    def test_preparar_y_aplicar(self):
        adr = self.nueva("decisiones-de-arquitectura", "adr", "usar-postgres")
        s = self.s("revision-humana", "revisar.py")
        self.assertIn(adr.stem, correr(s, "pendientes", cwd=self.app).stdout)
        self.assertEqual(correr(s, "preparar", cwd=self.app).returncode, 0)
        revision = self.trabajo("revision-humana") / "REVISION.md"
        texto = revision.read_text(encoding="utf-8")
        fila = next(l for l in texto.splitlines() if adr.stem in l)
        revision.write_text(texto.replace(fila, fila.rstrip().rstrip("|").rstrip() + " aceptada |"), encoding="utf-8")
        r = correr(s, "aplicar", "--humano", cwd=self.app, persona=False)
        self.assertIn("solo una persona", r.stderr)
        r = correr(s, "aplicar", "--humano", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (aceptada,) = self.trabajo("decisiones-de-arquitectura").rglob(f"{adr.stem}.md")
        self.assertEqual(aceptada.parent.name, "completadas")
        self.assertNotIn(adr.stem, correr(s, "pendientes", cwd=self.app).stdout)


class TestContratos(Base):
    PAQUETES = ["contratos-entre-repos"]

    def test_compara_con_el_repo_proveedor(self):
        proveedor = self.app.parent / "proveedor"
        proveedor.mkdir()
        repo.instalar(proveedor, ["rutas-de-api"])
        ruta = self.nueva("rutas-de-api", "ruta", "listar-pedidos", app=proveedor)
        campo(ruta, "path", "/orders")
        self.ajustes("contratos-entre-repos", {"repo": "app", "otros_repos": ["../proveedor"]})
        contrato = self.nueva("contratos-entre-repos", "contrato", "pedidos")
        for clave, valor in {"id_compartido": "orders.list", "path": "/orders", "proveedor": "proveedor", "ficha_proveedor": ruta.stem}.items():
            campo(contrato, clave, valor)
        self.assertEqual(self.estado("contratos-entre-repos", contrato, "vigente").returncode, 0)
        verificar = self.s("contratos-entre-repos", "verificar-contratos.py")
        r = correr(verificar, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        (vigente,) = self.trabajo("contratos-entre-repos").rglob(f"{contrato.stem}.md")
        campo(vigente, "path", "/pedidos")
        r = correr(verificar, cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no documenta", r.stderr)
        self.assertEqual(correr(self.s("contratos-entre-repos", "contratos.py"), "registro", cwd=self.app).returncode, 0)
        self.assertIn("orders.list", (self.trabajo("contratos-entre-repos") / "REGISTRO.md").read_text(encoding="utf-8"))


class TestCapas(Base):
    PAQUETES = ["arquitectura-por-capas"]

    def test_imports_entre_capas_y_modulos(self):
        m = "src/modules"
        self.escribir(f"{m}/orders/application/crear.usecase.ts", "import { Pedido } from '../domain/pedido';\n")
        self.escribir(f"{m}/orders/domain/pedido.ts", "import { db } from '../infrastructure/db';\n")
        self.escribir(f"{m}/orders/application/cobrar.usecase.ts", "import { pagar } from '../../payments/application/pagar';\n")
        self.escribir(f"{m}/orders/integrations/payments.integration.ts", "import { pagar } from '../../payments/application/pagar';\n")
        self.escribir(f"{m}/orders/orders.module.ts", "import { PaymentsModule } from '../payments/payments.module';\n")
        self.escribir("src/common/log.ts", "import { Pedido } from '@/modules/orders/domain/pedido';\nimport x from 'lodash';\n")
        self.escribir(f"{m}/orders/domain/reglas.py", "from ..infrastructure import db\nimport os\n")
        r = correr(self.s("arquitectura-por-capas", "capas.py"), "revisar", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("4 imports fuera de las reglas", r.stdout)
        self.assertIn("domain/pedido.ts:1: «domain» no puede importar «infrastructure»", r.stdout)
        self.assertIn("cruce de módulo orders → payments", r.stdout)
        self.assertIn("src/common/log.ts:1: el código común", r.stdout)
        self.assertIn("reglas.py:1", r.stdout)
        verificar = self.s("arquitectura-por-capas", "verificar-capas.py")
        self.assertEqual(correr(verificar, cwd=self.app).returncode, 0)
        self.ajustes("arquitectura-por-capas", {"nivel": "bloqueante"})
        self.assertEqual(correr(verificar, cwd=self.app).returncode, 1)
        self.assertIn("orders: application, domain, integrations", correr(self.s("arquitectura-por-capas", "capas.py"), "mapa", cwd=self.app).stdout)


class TestVivas(Base):
    PAQUETES = ["verificaciones-vivas", "rutas-de-api", "decisiones-de-arquitectura", "auditorias-tecnicas"]

    def test_revisiones_e_informe(self):
        self.escribir("src/orders/orders.controller.ts",
                      "import axios from 'axios';\n@Controller('orders')\nexport class C {\n  @Get(':id')\n  uno() {}\n  @Post()\n  crear() {}\n}\n")
        uno = self.nueva("rutas-de-api", "ruta", "ver-pedido")
        campo(uno, "path", "/orders/{id}")
        borrar = self.nueva("rutas-de-api", "ruta", "borrar-pedido")
        campo(borrar, "method", "DELETE")
        campo(borrar, "path", "/orders/:id")
        with uno.open("a", encoding="utf-8") as f:
            f.write("\n## Archivos ancla\n- `src/orders/orders.controller.ts`\n- `src/orders/viejo.service.ts`\n\nVer ADR-20990101-no-existe.\n")
        adr = self.nueva("decisiones-de-arquitectura", "adr", "sin-axios")
        campo(adr, "comprobacion_prohibido", '"from .axios."')
        campo(adr, "aplica_a", "[src/**/*.ts]")
        self.assertEqual(self.estado("decisiones-de-arquitectura", adr, "aceptada").returncode, 0)
        s = self.s("verificaciones-vivas", "vivas.py")
        r = correr(s, "--informe", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        for esperado in ("ruta sin ficha: POST /orders", "ficha activa sin ruta en el código: DELETE /orders/{}",
                         "ancla rota: src/orders/viejo.service.ts", f"{adr.stem} prohíbe", "id colgante: ADR-20990101-no-existe"):
            self.assertIn(esperado, r.stdout)
        self.assertNotIn("GET /orders/{}", r.stdout.split("ficha activa")[0])
        (aud,) = self.trabajo("auditorias-tecnicas").rglob("AUD-*-vivas-*.md")
        texto = aud.read_text(encoding="utf-8")
        self.assertIn("findings_count: 5", texto)
        self.assertIn("severidad: alta", texto)
        self.assertEqual(correr(self.s("auditorias-tecnicas", "verificar.py"), cwd=self.app).returncode, 0)

    def test_humo_solo_con_ejecutar(self):
        self.ajustes("verificaciones-vivas", {"humo": [{"nombre": "arranque", "comando": "exit 3"}]})
        s = self.s("verificaciones-vivas", "vivas.py")
        r = correr(s, "humo", cwd=self.app)
        self.assertEqual(r.returncode, 0)
        self.assertIn("sin ejecutar", r.stdout)
        r = correr(s, "humo", "--ejecutar", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("humo «arranque» falla (código 3)", r.stdout)


class TestRiqueza(Base):
    PAQUETES = ["instrucciones-aprobadas", "calidad-de-codigo", "memoria-e-historial"]

    def test_variantes_estado_y_tokens(self):
        fichas = self.s("instrucciones-aprobadas", "fichas.py")
        r = correr(fichas, "nueva", "instruccion", "--slug", "x", "--variante", "rara", cwd=self.app)
        self.assertIn("variante desconocida", r.stderr)
        self.assertEqual(correr(fichas, "nueva", "instruccion", "--slug", "docs", "--variante", "solo-docs", cwd=self.app).returncode, 0)
        (ins,) = self.trabajo("instrucciones-aprobadas").rglob("INS-*-docs.md")
        self.assertIn("tipo: solo-docs", ins.read_text(encoding="utf-8"))
        ciclo = self.s("instrucciones-aprobadas", "ciclo.py")
        self.assertEqual(correr(ciclo, "aprobar", ins.stem, "--humano", cwd=self.app).returncode, 0)
        self.assertEqual(correr(ciclo, "contexto", ins.stem, cwd=self.app).returncode, 0)
        estado = self.trabajo("instrucciones-aprobadas") / "ESTADO.md"
        estado.write_text("# Estado\n\n## Notas\n- nota de la persona\n", encoding="utf-8")
        self.assertEqual(correr(ciclo, "cerrar", ins.stem, cwd=self.app).returncode, 0)
        texto = estado.read_text(encoding="utf-8")
        self.assertIn(f"| Última cerrada | {ins.stem}", texto)
        self.assertRegex(texto, rf"\| {ins.stem} \| .* \| \d+ \|")
        self.assertIn("nota de la persona", texto)
        self.assertEqual(correr(ciclo, "estado", cwd=self.app).returncode, 0)
        self.assertEqual(estado.read_text(encoding="utf-8").count("<!-- uxyngraphar:estado -->"), 1)
        self.assertEqual(correr(self.s("instrucciones-aprobadas", "verificar-ciclo.py"), cwd=self.app).returncode, 0)

    def test_glosario_y_archivo_fuera_de_ia(self):
        glosario = self.s("calidad-de-codigo", "glosario.py")
        self.assertIn("vacío", correr(glosario, "terminos", cwd=self.app).stdout)
        ruta = Path(correr(glosario, "iniciar", cwd=self.app).stdout.strip())
        with ruta.open("a", encoding="utf-8") as f:
            f.write("| `expediente` | case file | Carpeta de un trámite | dominio | negocio | ana |\n")
        self.assertEqual(correr(glosario, "terminos", cwd=self.app).stdout.strip(), "expediente")
        deny = json.loads((self.app / ".claude/settings.json").read_text())["permissions"]["deny"]
        self.assertIn("Edit(uxyngraphar/trabajo/calidad-de-codigo/GLOSARIO.md)", deny)
        self.assertIn("uxyngraphar/trabajo/memoria-e-historial/archivo/**", (self.app / ".cursorignore").read_text(encoding="utf-8"))
        viejo = self.app / "viejo.md"
        viejo.write_text("decision antigua\n", encoding="utf-8")
        memoria = self.s("memoria-e-historial", "memoria.py")
        self.assertEqual(correr(memoria, "archivar", str(viejo), "--humano", cwd=self.app).returncode, 0)
        self.assertEqual(correr(memoria, "buscar", "antigua", cwd=self.app).stdout, "")
        self.assertNotEqual(correr(memoria, "buscar", "antigua", "--archivo", cwd=self.app).returncode, 0)
        self.assertIn("decision antigua", correr(memoria, "buscar", "antigua", "--archivo", "--humano", cwd=self.app).stdout)


if __name__ == "__main__":
    unittest.main()
