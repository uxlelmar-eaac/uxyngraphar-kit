"""Contrato de compatibilidad: lo que una versión nueva del pack NUNCA puede quitar ni cambiar.

Los ganchos de git, el workflow de CI y los comandos que un proyecto ya tiene escritos (de cualquier versión anterior)
llaman a estos scripts con estas opciones. Si una versión los quitara, esos proyectos se romperían al actualizar.
Regla: la lista solo crece. Renombrar un script = dejar el nombre viejo como alias que llama al nuevo.
`test_contrato.py` lo comprueba en el repo fuente; `probar()` lo comprueba en cada proyecto al actualizar (prueba de humo).
"""

from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# script (en <docs>/scripts/) → opciones que debe seguir aceptando
ENTRADAS: dict[str, tuple[str, ...]] = {
    "verificar-nucleo.py": ("--docs", "--repo", "--warn"),
    "validar-documentacion.py": (),
    "controlar.py": ("--staged", "--mensaje", "--base", "--docs", "--estricto"),
    "escanear-secretos.py": ("--docs", "--repo", "--historia"),
    "doctor.py": ("--fix", "--docs", "--repo", "--json"),
    "actualizar-pack.py": ("--apply", "--repo", "--docs", "--restaurar-nucleo", "--migracion-aprobada", "--evo"),
    "instalar-ganchos.py": ("--docs", "--quitar", "--pre-push", "--base"),
    "instalar-pack.py": ("--repo", "--docs", "--perfil", "--adoptar", "--proteger", "--dry-run"),
    "respaldos.py": ("listar", "ver", "restaurar", "limpiar", "--aplicar", "--docs", "--repo"),
    "contexto.py": ("--docs", "--repo", "--max-tokens"),
    "presupuesto.py": ("--docs", "--repo", "--max-tokens"),
    "costo-tokens.py": (),
    "empaquetar-pack.py": (),
    "espejo-mapa.py": (),
    "exportar-evo.py": (),
    "flota.py": (),
    "verificar-espejo.py": (),
    "memoria.py": ("buscar", "ver", "guardar", "recuperar", "purgar", "verificar", "--docs", "--repo"),
    "ajustes.py": ("crear", "listar", "verificar", "revisado", "retirar", "--evo", "--docs", "--repo"),
    "feedback.py": ("estado", "previsualizar", "activar", "enviar", "revocar", "--docs", "--repo"),
    "reglas.py": ("listar", "validar", "indice", "--docs", "--repo"),
}
ESPERA = 120   # segundos por comprobación


def _correr(args: list[str], cwd: Path) -> tuple[int, str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=ESPERA, stdin=subprocess.DEVNULL, env=env)
    except subprocess.TimeoutExpired:
        return -1, "no respondió en {} s".format(ESPERA)
    return r.returncode, r.stdout + r.stderr


def _ultima_linea_error(salida: str) -> str:
    lineas = [l for l in salida.strip().splitlines() if l.strip()]
    return lineas[-1].strip()[:200] if lineas else "sin salida"


def comprobaciones(repo: Path, docs: str) -> dict[str, list[str]]:
    """nombre → argumentos. Solo lo que existe en el proyecto (un pack antiguo puede no tener todas las entradas)."""
    scripts = repo / docs / "scripts"
    salida = {f"{s} --help": [str(scripts / s), "--help"] for s in ENTRADAS if (scripts / s).is_file()}
    if (scripts / "doctor.py").is_file():
        salida["doctor.py (diagnóstico)"] = [str(scripts / "doctor.py"), "--docs", docs]
    if (scripts / "validar-documentacion.py").is_file():
        salida["validar-documentacion.py (validación)"] = [str(scripts / "validar-documentacion.py"), docs]
    if (scripts / "controlar.py").is_file():
        salida["controlar.py (puerta)"] = [str(scripts / "controlar.py"), "--staged", "--docs", docs]
    return salida


def _evaluar(nombre: str, args: list[str], repo: Path) -> str | None:
    """None si funciona; si no, por qué. Un hallazgo del proyecto (salida 1) no es un fallo: un error de Python sí."""
    codigo, salida = _correr(args, repo)
    if codigo == -1:
        return f"{nombre}: {salida}"
    if "Traceback (most recent call last)" in salida:
        return f"{nombre}: error de Python ({_ultima_linea_error(salida)})"
    if nombre.endswith(" --help"):
        if codigo != 0:
            return f"{nombre}: terminó con código {codigo}"
        faltan = [o for o in ENTRADAS[nombre[:-7]] if o not in salida]
        if faltan:
            return f"{nombre}: ya no acepta {', '.join(faltan)}"
    elif codigo not in (0, 1):
        return f"{nombre}: terminó con código {codigo} ({_ultima_linea_error(salida)})"
    return None


def probar(repo: Path, docs: str) -> list[str]:
    """Ejecuta las herramientas del proyecto tal como las usan los ganchos y el CI. Devuelve los fallos (vacío = todo arranca)."""
    pruebas = comprobaciones(repo, docs)
    with ThreadPoolExecutor(max_workers=min(8, len(pruebas) or 1)) as ex:
        resultados = list(ex.map(lambda par: _evaluar(par[0], par[1], repo), pruebas.items()))
    return sorted(r for r in resultados if r)


def clave(fallo: str) -> str:
    return fallo.split(":", 1)[0]
