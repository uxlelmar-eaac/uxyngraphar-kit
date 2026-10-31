"""Pruebas del instalador de una línea contra una «release» falsa servida en 127.0.0.1 (sin internet)."""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ES / "instalador"))
_spec = importlib.util.spec_from_file_location("publicar_uxy", ES / "_compartido" / "publicar.py")
publicar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(publicar)

import arranque  # noqa: E402

VERSION = publicar.comprobar_versiones("")
WINDOWS = os.name == "nt"


def publicar_version(destino: Path, version: str = VERSION) -> Path:
    """Genera los archivos de una release. Para otra versión, copia el repo y cambia VERSION.md en los tres sitios."""
    if version == VERSION:
        publicar.publicar(destino, verificar_packs=False)
        return destino
    copia = destino.parent / f"src-{version}"
    shutil.copytree(ES, copia / "español", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".decisiones"))
    for c in ("backend", "frontend", "_compartido/base"):
        f = copia / "español" / c / "VERSION.md"
        f.write_text(f.read_text(encoding="utf-8").replace(f"version: {VERSION}", f"version: {version}"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(copia / "español" / "_compartido" / "publicar.py"), "--salida", str(destino)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return destino


class Entorno(unittest.TestCase):
    """Servidor con /download/vX/… y /latest/download/…, y un HOME falso para cada prueba."""

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.t = Path(self._t.name)
        self.srv = self.t / "srv"
        self.home = self.t / "home"
        self.home.mkdir()
        manejador = functools.partial(type("Q", (SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=str(self.srv))
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), manejador)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.uxy = self.home / ".uxyngraphar"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("UXYNGRAPHAR_")}
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home), SHELL="/bin/bash", UXYNGRAPHAR_URL_BASE=self.base, PYTHONIOENCODING="utf-8")
        if WINDOWS:   # en Windows no tocamos el PATH real del usuario de la máquina de pruebas
            self.env.update(UXYNGRAPHAR_HOME=str(self.uxy), UXYNGRAPHAR_SIN_PATH="1")

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self._t.cleanup()

    def servir(self, version: str = VERSION, ultima: bool = True) -> Path:
        dist = publicar_version(self.t / f"dist-{version}", version)
        for d in [self.srv / "download" / f"v{version}"] + ([self.srv / "latest" / "download"] if ultima else []):
            shutil.copytree(dist, d, dirs_exist_ok=True)
        return dist

    def instalador(self, version: str = VERSION) -> bytes:
        return (self.srv / "download" / f"v{version}" / "instalar-uxyngraphar.py").read_bytes()

    def por_tuberia(self, codigo: bytes, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-", *args], input=codigo, capture_output=True, env=self.env, cwd=self.t)

    def lanzador(self) -> Path:
        return self.uxy / "bin" / "uxyngraphar-lanzador.py" if WINDOWS else self.home / ".local" / "bin" / "uxyngraphar"

    def perfil(self) -> Path:
        """Archivo de inicio de la terminal que tocó el instalador (.bashrc en Linux, .bash_profile en macOS)."""
        import json
        return Path(json.loads((self.uxy / "instalacion.json").read_text(encoding="utf-8"))["perfil"])

    def uxyngraphar(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.lanzador()), *args], capture_output=True, text=True, env=self.env, encoding="utf-8")


class TestPublicado(Entorno):
    def test_ascii_python36_y_main_al_final(self):
        codigo = self.servir() and self.instalador()
        self.assertTrue(all(b < 128 for b in codigo), "el instalador publicado debe ser solo ASCII")
        import ast
        ast.parse(codigo.decode("ascii"), feature_version=(3, 6))
        self.assertTrue(codigo.rstrip().endswith(b"sys.exit(main())"))
        self.assertNotIn(b"solo-repositorio", codigo)
        self.assertIn(f'VERSION = "{VERSION}"'.encode(), codigo)

    def test_zip_sin_compartido_y_reproducible(self):
        a = publicar_version(self.t / "a")
        b = publicar_version(self.t / "b")
        za = a / f"uxyngraphar-{VERSION}.zip"
        self.assertEqual(za.read_bytes(), (b / za.name).read_bytes())
        nombres = zipfile.ZipFile(za).namelist()
        self.assertFalse([n for n in nombres if "/_compartido/" in n or "__pycache__" in n])
        self.assertIn(f"uxyngraphar-{VERSION}/uxyngraphar.py", nombres)


class TestInstalacion(Entorno):
    def test_home_propio_no_toca_local_bin_ni_perfil(self):
        """Con UXYNGRAPHAR_HOME propio (p. ej. una prueba en una carpeta temporal) el comando va dentro de esa carpeta."""
        self.servir()
        otra = self.t / "otra-casa"
        self.env.update(UXYNGRAPHAR_HOME=str(otra))
        self.env.pop("UXYNGRAPHAR_SIN_PATH", None)
        r = self.por_tuberia(self.instalador())
        self.assertEqual(r.returncode, 0, r.stdout.decode() + r.stderr.decode())
        self.assertFalse((self.home / ".local" / "bin").exists(), "no debe escribir en el ~/.local/bin de la persona")
        self.assertFalse([p.name for p in self.home.iterdir() if p.name.startswith((".bash", ".profile", ".zsh"))])
        lanzador = otra / "bin" / ("uxyngraphar-lanzador.py" if WINDOWS else "uxyngraphar")
        self.assertTrue(lanzador.is_file())
        v = subprocess.run([sys.executable, str(lanzador), "version"], capture_output=True, text=True, env=self.env, encoding="utf-8")
        self.assertIn(VERSION, v.stdout)

    def test_instala_por_tuberia(self):
        self.servir()
        r = self.por_tuberia(self.instalador())
        self.assertEqual(r.returncode, 0, r.stdout.decode() + r.stderr.decode())
        self.assertTrue((self.uxy / "versiones" / VERSION / ".completa").is_file())
        self.assertEqual((self.uxy / "actual").read_text().strip(), VERSION)
        v = self.uxyngraphar("version")
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertIn(VERSION, v.stdout)
        if not WINDOWS:
            self.assertTrue(os.access(self.lanzador(), os.X_OK))
            self.assertIn(arranque.BLOQUE_INI, self.perfil().read_text())

    @unittest.skipUnless(WINDOWS, "solo Windows")
    def test_lanzador_cmd_windows(self):
        self.servir()
        self.assertEqual(self.por_tuberia(self.instalador()).returncode, 0)
        cmd = self.uxy / "bin" / "uxyngraphar.cmd"
        r = subprocess.run([str(cmd), "version"], capture_output=True, text=True, env=self.env, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(VERSION, r.stdout)
        self.assertEqual(subprocess.run([str(cmd), "nada"], capture_output=True, env=self.env).returncode, 2, "el .cmd debe devolver el código de salida")

    @unittest.skipIf(WINDOWS or not shutil.which("curl"), "necesita curl en Linux/macOS")
    def test_curl_real_por_tuberia(self):
        self.servir()
        curl = subprocess.Popen(["curl", "-fsSL", f"{self.base}/latest/download/instalar-uxyngraphar.py"], stdout=subprocess.PIPE)
        r = subprocess.run([sys.executable, "-"], stdin=curl.stdout, capture_output=True, env=self.env)
        curl.wait()
        curl.stdout.close()
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        self.assertTrue((self.uxy / "versiones" / VERSION / ".completa").is_file())

    def test_segunda_vez_no_cambia_nada(self):
        self.servir()
        self.assertEqual(self.por_tuberia(self.instalador()).returncode, 0)
        marca = (self.uxy / "versiones" / VERSION / ".completa").stat().st_mtime_ns
        r = self.por_tuberia(self.instalador())
        self.assertEqual(r.returncode, 0)
        self.assertIn("nada que actualizar", r.stdout.decode())
        self.assertEqual((self.uxy / "versiones" / VERSION / ".completa").stat().st_mtime_ns, marca)
        if not WINDOWS:
            self.assertEqual(self.perfil().read_text().count(arranque.BLOQUE_INI), 1)

    def test_script_cortado_no_hace_nada(self):
        self.servir()
        codigo = self.instalador()
        ultima_linea = codigo.rstrip().rfind(b"\n")
        for corte in (len(codigo) // 4, len(codigo) // 2, ultima_linea, len(codigo.rstrip()) - 3):
            r = self.por_tuberia(codigo[:corte])
            self.assertFalse(self.uxy.exists(), f"cortado en {corte} escribió algo: {r.stdout!r}")
            self.assertNotIn(b"Descargando", r.stdout)

    def test_huella_incorrecta_no_instala(self):
        self.servir()
        z = self.srv / "download" / f"v{VERSION}" / f"uxyngraphar-{VERSION}.zip"
        z.write_bytes(z.read_bytes()[:-10] + b"0123456789")
        r = self.por_tuberia(self.instalador())
        self.assertEqual(r.returncode, 1)
        self.assertIn("huella", r.stderr.decode())
        self.assertFalse((self.uxy / "versiones" / VERSION).exists())
        self.assertFalse((self.uxy / "actual").exists())

    def test_zip_con_ruta_peligrosa_no_instala(self):
        self.servir()
        d = self.srv / "download" / f"v{VERSION}"
        z = d / f"uxyngraphar-{VERSION}.zip"
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr(f"uxyngraphar-{VERSION}/../../malo.txt", "x")
        sumas = (d / "SHA256SUMS").read_text().splitlines()
        nueva = hashlib.sha256(z.read_bytes()).hexdigest()
        (d / "SHA256SUMS").write_text("\n".join(f"{nueva}  {z.name}" if l.endswith(z.name) else l for l in sumas) + "\n")
        r = self.por_tuberia(self.instalador())
        self.assertEqual(r.returncode, 1)
        self.assertIn("ruta no permitida", r.stderr.decode())
        self.assertFalse(any(self.t.rglob("malo.txt")))

    def test_sin_red_explica_y_no_deja_nada(self):
        self.servir()
        codigo = self.instalador()
        self.env["UXYNGRAPHAR_URL_BASE"] = "http://127.0.0.1:9"
        r = self.por_tuberia(codigo)
        self.assertEqual(r.returncode, 1)
        self.assertIn("No pude descargar", r.stderr.decode())
        self.assertFalse((self.uxy / "versiones" / VERSION).exists())

    def test_version_inexistente(self):
        self.servir()
        r = self.por_tuberia(self.instalador(), "--version", "9.9.9")
        self.assertEqual(r.returncode, 1)
        self.assertIn("404", r.stderr.decode())

    def test_restos_de_un_corte_se_limpian(self):
        self.servir()
        (self.uxy / "versiones" / f"{VERSION}.tmp").mkdir(parents=True)
        (self.uxy / ".descarga-viejo").mkdir()
        self.assertEqual(self.por_tuberia(self.instalador()).returncode, 0)
        self.assertFalse((self.uxy / "versiones" / f"{VERSION}.tmp").exists())
        self.assertFalse((self.uxy / ".descarga-viejo").exists())

    def test_candado(self):
        self.servir()
        self.uxy.mkdir()
        candado = self.uxy / ".instalando"
        candado.touch()
        r = self.por_tuberia(self.instalador())
        self.assertEqual(r.returncode, 1)
        self.assertIn("otra instalación", r.stderr.decode())
        hace_una_hora = time.time() - 3600
        os.utime(candado, (hace_una_hora, hace_una_hora))
        self.assertEqual(self.por_tuberia(self.instalador()).returncode, 0)
        self.assertFalse(candado.exists())


class TestPiezas(unittest.TestCase):
    def test_python_viejo(self):
        self.assertIn("3.10", arranque.problema_python((3, 9, 6)))
        self.assertEqual(arranque.problema_python((3, 12, 0)), "")

    def test_perfil_ida_y_vuelta(self):
        with tempfile.TemporaryDirectory() as t:
            perfil = Path(t) / ".bashrc"
            perfil.write_text("alias ll='ls -l'\n")
            antiguo = dict(os.environ)
            os.environ.update(HOME=t, USERPROFILE=t, SHELL="/bin/bash")
            try:
                ruta = arranque.agregar_a_perfil(os.path.join(t, ".local", "bin"))
                arranque.agregar_a_perfil(os.path.join(t, ".local", "bin"))
                self.assertEqual(Path(ruta).read_text().count(arranque.BLOQUE_INI), 1)
                self.assertTrue(arranque.quitar_de_perfil(ruta))
                self.assertEqual(perfil.read_text(), "alias ll='ls -l'\n")
            finally:
                os.environ.clear()
                os.environ.update(antiguo)

    def test_rutas_del_zip(self):
        p = "uxyngraphar-1.0.0/"
        self.assertTrue(arranque.ruta_segura(p + "backend/README.md", p))
        for mala in (p + "../x", "/etc/passwd", "otra/x", p + "a\\..\\x", "C:/x", p + "a//b"):
            self.assertFalse(arranque.ruta_segura(mala, p), mala)


if __name__ == "__main__":
    unittest.main()
