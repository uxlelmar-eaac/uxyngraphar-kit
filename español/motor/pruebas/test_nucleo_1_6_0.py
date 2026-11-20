"""Núcleo implementado (1.6.0): compuerta «implementado», importación sin pérdidas con informe de preservación
(crear / adaptar), propuestas de mejora del sistema (PMS), reportar --mejora y flujos publicables."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import catalogo
import creador
import entrada
import especificacion as esp
import generar
import implementado
import importar
import reportes

base = esp.base
AQUI = Path(__file__).resolve().parent
WEB = AQUI.parent / "web"

SISTEMA = """# Revisión de pull requests

Revisa cada pull request del equipo antes de aprobarlo: exige pruebas, explica los riesgos con ejemplos concretos y
nunca aprueba cambios que toquen producción sin una persona.

## Rol del agente

Eres el revisor técnico del equipo: respondes de que ningún cambio entre sin pruebas ni con riesgos sin explicar.
Decides con el criterio de LIMITES.md y hablas claro y breve, sin adornos.

## Qué resuelve

Sin este sistema los pull requests se aprueban sin pruebas y los riesgos se descubren en producción.

## Problemas que cubre

- `aprobaciones-sin-pruebas`: pull requests aprobados sin pruebas que cubran el cambio.
- `riesgos-sin-explicar`: cambios con riesgos que nadie dejó escritos para quien revisa.

## Fuera de alcance

- Desplegar a producción: lo decide el sistema de despliegues.
- Diseñar la arquitectura del cambio: no lo cubre este sistema.

## Cuándo usarlo

- Al revisar un pull request antes de aprobarlo o pedir cambios.
- Al preparar un pull request propio para revisión.

## Cuándo no usarlo

- En ramas experimentales que nunca se van a fusionar con la principal.

## Entradas y salidas

- Entradas: el diff del pull request, su descripción y el resultado de la integración continua.
- Salidas: un informe en uxyngraphar/trabajo/revision-de-pull-requests/ con la decisión y los riesgos.

## Sistemas complementarios

- Ninguno por ahora: se combina con otros solo mediante flujos.
"""

LIMITES = """# Límites

Se cumplen en todo el trabajo del sistema. Romper uno lo decide una persona.

1. **No apruebes sin pruebas:** cada cambio de código trae pruebas que lo cubren; si faltan, pide cambios.
2. **Explica cada riesgo:** cada riesgo lleva un ejemplo concreto de cómo fallaría y cómo se mitiga.
3. **No toques producción:** ningún comando contra producción; si el cambio lo necesita, lo hace una persona.
4. **No edites el código del autor:** propones el cambio en el informe; el autor lo aplica.
5. **Cita la línea:** cada observación apunta al archivo y la línea del diff.

## Cuándo detenerse y preguntar

- El cambio toca datos de producción o credenciales.
- Las pruebas fallan por algo ajeno al pull request.
- No está claro qué pidió la persona que abrió el pull request.
"""

MEMORIAS = """# Memorias

Lo que conviene recordar del equipo al revisar sus pull requests.

## Qué recordar

- Qué carpetas no necesitan pruebas (generadas, migraciones) según el equipo.
- Qué riesgos aceptó una persona y por qué.
- Quién aprueba los cambios de infraestructura.

## Qué no recordar

- El contenido de los diffs: se lee en cada pull request.
- Resultados de la integración continua: caducan enseguida.
"""

PERMISOS = """# Permisos

Qué hace el agente solo y qué decide una persona.

<!-- uxyngraphar:permisos:inicio -->
<!-- uxyngraphar:permisos:fin -->

## Por qué

- Aprobar o archivar memorias lo hace una persona: son acuerdos del equipo, no del agente.
"""

README_AUTOR = """
## En una frase

Revisa pull requests con pruebas obligatorias y riesgos explicados.

## Cómo se pide

- «usa el sistema revision-de-pull-requests y revisa el PR 42».
"""

FASE = """---
fase: {fase}
resuelve: [aprobaciones-sin-pruebas, riesgos-sin-explicar]
skills: [revisar-diff]
---

# Fase: {fase}

## Objetivo

Dejar el pull request revisado con una decisión clara y los riesgos escritos.

## Pasos

1. Lee la descripción del pull request y el resultado de la integración continua.
2. Recorre el diff con la skill `revisar-diff` y anota cada observación con su archivo y línea.
3. Escribe el informe en uxyngraphar/trabajo/revision-de-pull-requests/ con la decisión.

## Criterio de salida

- Hay un informe con decisión (aprobar o pedir cambios) y cada riesgo con su ejemplo.
"""

SKILL = """---
name: revisar-diff
description: Recorre un diff y anota observaciones con archivo y línea; úsala cuando una fase lo pida.
resuelve: [aprobaciones-sin-pruebas, riesgos-sin-explicar]
---

# Revisar diff

## Cuándo usarla

Cuando una fase pide recorrer el diff de un pull request.

## Pasos

1. Abre el diff archivo por archivo.
2. Comprueba que cada cambio tiene su prueba.
3. Anota cada riesgo con un ejemplo concreto.
"""

EJEMPLO = """# Ejemplo: PR 42 sin pruebas

La persona pidió revisar el PR 42, que cambiaba el cálculo de impuestos sin pruebas. El agente pidió cambios: añadir una
prueba por tramo y explicar el riesgo de redondeo con un ejemplo de 0,005.
"""


def _hash_carpeta(c: Path) -> dict[str, str]:
    return {p.relative_to(c).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(c.rglob("*")) if p.is_file()}


def sistema_implementado(raiz: Path, pid: str = "revision-de-pull-requests") -> Path:
    c = catalogo.crear(pid, "Revisión de pull requests", "Revisa pull requests", raiz, familia="proceso")
    m = base.leer_manifiesto(c)
    m["activacion"] = [pid, "revision de pull requests", "revisar un pr"]
    m["alcance"] = {"problemas": [{"id": "aprobaciones-sin-pruebas", "descripcion": "PR aprobados sin pruebas"},
                                  {"id": "riesgos-sin-explicar", "descripcion": "Riesgos sin explicar"}],
                    "fuera_de_alcance": [{"tema": "Desplegar a producción", "derivar_a": None},
                                         {"tema": "Diseñar la arquitectura", "derivar_a": None}]}
    for f in list((c / "proceso").glob("*.md")):
        f.unlink()
    for nombre in ("preparar", "revisar", "cerrar"):
        (c / "proceso" / f"{nombre}.md").write_text(FASE.format(fase=nombre), encoding="utf-8")
    m["proceso"] = ["preparar", "revisar", "cerrar"]
    shutil.rmtree(c / "skills")
    for nombre in ("revisar-diff", "revisar-riesgos"):
        (c / "skills" / nombre).mkdir(parents=True)
        (c / "skills" / nombre / "SKILL.md").write_text(SKILL.replace("revisar-diff", nombre), encoding="utf-8")
    for f in list((c / "ejemplos").glob("*.md")):
        f.unlink()
    (c / "ejemplos" / "pr-sin-pruebas.md").write_text(EJEMPLO, encoding="utf-8")
    for f in list((c / "referencia").glob("*.md")):
        f.write_text("# Guía\n\nCómo leer un diff grande: por carpetas, de lo compartido a lo particular.\n", encoding="utf-8")
    (c / "HERRAMIENTAS.md").write_text("# Herramientas\n\nEste sistema no trae scripts propios: usa los comunes "
                                       "(`scripts/comun/verificar.py`, `memorias.py` y `mejoras.py`).\n", encoding="utf-8")
    (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (c / base.DESCRIPCION).write_text(SISTEMA, encoding="utf-8")
    (c / base.LIMITES).write_text(LIMITES, encoding="utf-8")
    (c / base.MEMORIAS).write_text(MEMORIAS, encoding="utf-8")
    (c / base.PERMISOS).write_text(PERMISOS, encoding="utf-8")
    (c / base.ENTRADA).write_text("# Revisión de pull requests\n" + README_AUTOR, encoding="utf-8")
    entrada.actualizar(c)
    return c


class Compuerta(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_esqueleto_recien_creado_no_esta_implementado(self):
        c = catalogo.crear("esqueleto-de-prueba", "Esqueleto de prueba", "", self.tmp)
        r = implementado.evaluar(c)
        self.assertFalse(r["implementado"])
        self.assertTrue(any("sin rellenar" in e for e in r["errores"]))
        self.assertTrue(any("LIMITES.md" in e for e in r["errores"]))

    def test_base_trae_rol_del_agente_y_la_regla_de_no_editar(self):
        self.assertIn("## Rol del agente", (esp.PLANTILLA / base.DESCRIPCION).read_text(encoding="utf-8"))
        self.assertIn("mejoras.py nueva", (esp.PLANTILLA / base.LIMITES).read_text(encoding="utf-8"))

    def test_sistema_completo_esta_implementado(self):
        c = sistema_implementado(self.tmp)
        r = implementado.evaluar(c)
        self.assertEqual(r["errores"], [], r)
        self.assertTrue(r["implementado"])
        self.assertEqual(r["metricas"]["fases"], 3)
        self.assertEqual(esp.validar_sistema(c), [])

    def test_faltan_minimos(self):
        c = sistema_implementado(self.tmp)
        (c / base.LIMITES).write_text("# Límites\n\n1. Una sola regla larga y comprobable para la prueba.\n", encoding="utf-8")
        r = implementado.evaluar(c)
        self.assertFalse(r["implementado"])
        self.assertTrue(any("reglas numeradas" in e for e in r["errores"]))
        self.assertTrue(any("detenerse" in e for e in r["errores"]))

    def test_rol_por_introduccion_tambien_vale(self):
        c = sistema_implementado(self.tmp)
        texto = (c / base.DESCRIPCION).read_text(encoding="utf-8")
        inicio = texto.index("## Rol del agente")
        fin = texto.index("## Qué resuelve")
        (c / base.DESCRIPCION).write_text(texto[:inicio] + texto[fin:], encoding="utf-8")
        self.assertTrue(implementado.evaluar(c)["implementado"])
        (c / base.DESCRIPCION).write_text("# Revisión de pull requests\n\n" + texto[fin:], encoding="utf-8")
        self.assertTrue(any("Rol del agente" in e for e in implementado.evaluar(c)["errores"]))

    def test_citar_otro_sistema_es_error(self):
        c = sistema_implementado(self.tmp)
        ruta = c / "skills" / "revisar-diff" / "SKILL.md"
        ruta.write_text(ruta.read_text(encoding="utf-8") + "\n4. Ejecuta `python3 uxyngraphar/sistemas-de-gobernanza/otro-sistema/scripts/x.py`.\n",
                        encoding="utf-8")
        r = implementado.evaluar(c)
        self.assertTrue(any("otro sistema" in e and "otro-sistema" in e for e in r["errores"]))

    def test_todo_en_minusculas_no_es_marcador(self):
        c = sistema_implementado(self.tmp)
        (c / base.LIMITES).write_text(LIMITES.replace("cada cambio", "todo cambio"), encoding="utf-8")
        self.assertTrue(implementado.evaluar(c)["implementado"])

    def test_creador_validar_incluye_implementado(self):
        sistema_implementado(self.tmp)
        r = creador.validar(self.tmp)
        self.assertTrue(r["implementado"]["implementado"])


class Importacion(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cat = self.tmp / "catalogo"
        self.cat.mkdir()

    def _origen_sistema(self) -> Path:
        origen = sistema_implementado(self.tmp / "fuente")
        shutil.rmtree(origen / "scripts")   # como en un catálogo fuente: scripts/comun lo pone la construcción
        (origen / "pruebas" / "__pycache__").mkdir(exist_ok=True)
        (origen / "pruebas" / "__pycache__" / "x.pyc").write_bytes(b"\x00basura")
        return origen

    def test_adaptar_conserva_todo_y_no_toca_el_origen(self):
        origen = self._origen_sistema()
        antes = _hash_carpeta(origen)
        r = importar.importar(importar.desde_carpeta(origen), raiz=self.cat)
        self.assertEqual(_hash_carpeta(origen), antes, "el origen no se toca")
        self.assertEqual(r["modo"], "adaptar")
        p = r["preservacion"]
        self.assertEqual(p["conservados"], p["total"])
        self.assertEqual(p["perdidos"], [])
        destino = Path(r["ruta"])
        cambiados = {f["destino"] for f in p["archivos"] if f["estado"] != "identico"}
        self.assertLessEqual(cambiados, set(base.NUCLEO), cambiados)
        nuevos = set(base.archivos_del_sistema(destino)) - {k for k in antes if "__pycache__" not in k}
        self.assertTrue(all(n.startswith("scripts/comun/") for n in nuevos), nuevos)
        self.assertTrue(r["implementado"]["implementado"], r["implementado"])

    def test_crear_desde_documentos_sueltos(self):
        docs = {"notas/reglas.md": b"# Reglas\n\nNunca aprobar sin pruebas.\n", "ideas.txt": b"Revisar riesgos."}
        self.assertEqual(importar.detectar_modo(docs), "crear")
        r = importar.importar(docs, pid="mis-reglas", raiz=self.cat)
        self.assertEqual(r["modo"], "crear")
        self.assertEqual(r["preservacion"]["identicos"], 2)
        self.assertFalse(r["implementado"]["implementado"])   # la base deja huecos: uxyn los completa

    def test_crear_sin_arranque_redundante(self):
        origen = self._origen_sistema()
        r = importar.importar(importar.desde_carpeta(origen), raiz=self.cat, modo="crear")
        destino = Path(r["ruta"])
        self.assertFalse((destino / "skills" / "accion-principal").exists())
        self.assertEqual(base.leer_manifiesto(destino)["proceso"], ["preparar", "revisar", "cerrar"])

    def test_modo_invalido(self):
        with self.assertRaises(importar.ImportacionInvalida):
            importar.importar({"a.md": b"x"}, pid="a-b", raiz=self.cat, modo="otro")


class Mejoras(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.proyecto = self.tmp / "proyecto"
        fuente = sistema_implementado(self.tmp / "cat")
        self.sistema = self.proyecto / base.CARPETA_SISTEMAS_DE_GOBERNANZA / fuente.name
        shutil.copytree(fuente, self.sistema)

    def test_nueva_propuesta_en_su_carpeta_reservada(self):
        import uxyn_mejoras as mejoras
        diff = "--- a/LIMITES.md\n+++ b/LIMITES.md\n@@ -1 +1 @@\n-x\n+y\n"
        ruta = mejoras.crear(self.sistema, "falta-regla", "Falta una regla de secretos", "No dice qué hacer con secretos en el diff.",
                             archivo="LIMITES.md", diff=diff)
        self.assertEqual(ruta.parent, self.proyecto / base.CARPETA_TRABAJO / self.sistema.name / base.CARPETA_MEJORAS)
        self.assertTrue(ruta.name.startswith("PMS-"))
        texto = ruta.read_text(encoding="utf-8")
        self.assertIn("```diff", texto)
        self.assertEqual(mejoras.listar(self.sistema)[0].status, "borrador")

    def test_diff_fuera_del_sistema_se_rechaza(self):
        import uxyn_mejoras as mejoras
        with self.assertRaises(ValueError):
            mejoras.crear(self.sistema, "codigo", "Toca código", "Un diff del código del proyecto.",
                          diff="--- a/src/app.ts\n+++ b/src/app.ts\n@@ -1 +1 @@\n-a\n+b\n")

    def test_reportar_mejora_admite_mas_texto_y_marca_enviada(self):
        import uxyn_mejoras as mejoras
        ruta = mejoras.crear(self.sistema, "larga", "Propuesta larga", "x" * 5000)
        _, propuesta = reportes.propuesta_instalada("yo/revision-de-pull-requests", ruta.stem, self.proyecto)
        datos = reportes.armar("yo/revision-de-pull-requests", "mejora", propuesta.cuerpo)
        self.assertEqual(datos["tipo"], "MEJORA")
        with self.assertRaises(ValueError):
            reportes.armar("yo/revision-de-pull-requests", "problema", "x" * 5000)
        mejoras.marcar_enviada(propuesta)
        self.assertEqual(mejoras.listar(self.sistema)[0].status, "enviada")

    def test_prefijo_y_carpeta_reservados_para_fichas(self):
        errores = base._validar_fichas({"x": {"carpeta": base.CARPETA_MEJORAS, "prefijo": base.PREFIJO_MEJORA,
                                              "plantilla": "plantillas/x.md", "inicial": "a", "status_validos": ["a"]}})
        self.assertTrue(any("propuestas de mejora" in e for e in errores))

    def test_agentes_md_dice_como_proponer(self):
        self.assertIn("mejoras.py nueva", generar.bloque([]))
        self.assertIn("--mejora", generar.bloque([]))

    def test_script_comun_mejoras(self):
        self.assertTrue((esp.COMUN / "mejoras.py").is_file())
        self.assertTrue((esp.COMUN / "uxyn_mejoras.py").is_file())


class FlujosPublicables(unittest.TestCase):
    def test_solo_con_sistemas_publicados(self):
        import flujos_guardados as g
        datos = {"id": "mi-flujo", "nombre": "Mi flujo", "sistemas": ["a-b", "c-d"], "flujo": {"modo": "secuencia", "secuencia": ["a-b", "c-d"]}}
        with mock.patch.object(g, "leer", return_value=datos), \
                mock.patch("remoto.versiones_disponibles", return_value={"a-b": {"editor": "yo"}}):
            with self.assertRaises(ValueError):
                g.para_publicar("mi-flujo")
        with mock.patch.object(g, "leer", return_value=datos), \
                mock.patch("remoto.versiones_disponibles", return_value={"a-b": {"editor": "yo"}, "c-d": {"editor": "otra"}}):
            r = g.para_publicar("mi-flujo")
        self.assertEqual(r["sistemas"], [{"editor": "yo", "id": "a-b"}, {"editor": "otra", "id": "c-d"}])
        self.assertEqual(r["flujo"]["modo"], "secuencia")


class Panel(unittest.TestCase):
    def test_empezar_con_uxyn_importa_sin_perdidas(self):
        js = (WEB / "js" / "vistas" / "creador-inicio.js").read_text(encoding="utf-8")
        self.assertNotIn("archivos núcleo", js)
        self.assertIn("/api/catalogo/importar", js)
        self.assertIn("prefijoImportado", js)

    def test_insignia_implementado(self):
        js = (WEB / "js" / "vistas" / "mis-sistemas.js").read_text(encoding="utf-8")
        self.assertIn("Implementado ✓", js)

    def test_mercado_muestra_estrellas(self):
        js = (WEB / "js" / "vistas" / "catalogo.js").read_text(encoding="utf-8")
        self.assertIn("estrellas", js)


if __name__ == "__main__":
    unittest.main()
