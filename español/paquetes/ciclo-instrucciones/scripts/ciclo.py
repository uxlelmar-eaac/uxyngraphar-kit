#!/usr/bin/env python3
"""Ciclo de una instrucción.

  python3 uxyngraphar/paquetes/ciclo-instrucciones/scripts/ciclo.py aprobar <id> --humano   (solo una persona)
  python3 uxyngraphar/paquetes/ciclo-instrucciones/scripts/ciclo.py contexto <id> [--max-tokens N]
  python3 uxyngraphar/paquetes/ciclo-instrucciones/scripts/ciclo.py cerrar <id>
  python3 uxyngraphar/paquetes/ciclo-instrucciones/scripts/ciclo.py pendientes

Códigos: 0 ok · 1 error de uso · 2 no encontrada · 3 la instrucción no está aprobada o incumple el alcance.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import ciclo_reglas as reglas  # noqa: E402
import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
TOKENS_POR_CARACTER = 0.25
LINEAS_SIN_RANGO = 200


def _instruccion(fid: str) -> tuple[fichas.Ficha, dict]:
    f = fichas.buscar(PAQUETE, fid)
    if f.tipo != "instruccion":
        raise ValueError(f"«{fid}» no es una instrucción")
    fm, _ = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
    return f, fm


def _campo(ruta: Path, clave: str, valor: str) -> None:
    ruta.write_text(base.escribir_campo(ruta.read_text(encoding="utf-8"), clave, valor), encoding="utf-8")


def aprobar(fid: str, por_humano: bool) -> Path:
    f, fm = _instruccion(fid)
    if f.status != "awaiting_approval":
        raise ValueError(f"solo se aprueba desde awaiting_approval (está en {f.status})")
    problemas = reglas.problemas_alcance(fm, base.leer_ajustes(PAQUETE))
    if problemas:
        raise ValueError("no se puede aprobar: " + "; ".join(problemas))
    destino = fichas.cambiar_estado(PAQUETE, fid, "approved", por_humano)
    _campo(destino, "approved_at", reglas.ahora())
    return destino


def _fragmento(raiz: Path, ancla: str) -> tuple[str, str]:
    ruta, inicio, fin = reglas.separar_ancla(ancla)
    archivo = (raiz / ruta).resolve()
    if raiz.resolve() not in archivo.parents or not archivo.is_file():
        return f"{ancla} (NO EXISTE)", ""
    lineas = archivo.read_text(encoding="utf-8", errors="replace").splitlines()
    inicio, fin = (inicio, fin) if inicio else (1, min(len(lineas), LINEAS_SIN_RANGO))
    cuerpo = "\n".join(f"{n:>5}| {lineas[n - 1]}" for n in range(inicio, min(fin, len(lineas)) + 1))
    return f"{ruta}:{inicio}-{fin}", cuerpo


def contexto(fid: str, max_tokens: int) -> tuple[int, str]:
    f, fm = _instruccion(fid)
    texto_ficha = f.ruta.read_text(encoding="utf-8")
    if f.status != "approved":
        return 3, f"BLOQUEADO: la instrucción está en «{f.status}»; necesita aprobación de una persona.\n\n{texto_ficha}"
    problemas = reglas.problemas_alcance(fm, base.leer_ajustes(PAQUETE))
    if problemas:
        return 3, "BLOQUEADO (alcance): " + "; ".join(problemas) + f"\n\n{texto_ficha}"
    raiz = base.raiz_app(PAQUETE)
    partes = [("FICHA " + f.ruta.relative_to(raiz).as_posix(), texto_ficha)]
    for doc in reglas.lista(fm.get("lectura_minima")):
        partes.append(_fragmento(raiz, doc))
    for ancla in reglas.lista(fm.get("anclas_codigo")):
        partes.append(_fragmento(raiz, ancla))
    salida, usados, omitidos = [], 0, []
    for titulo, cuerpo in partes:
        coste = int(len(cuerpo) * TOKENS_POR_CARACTER) + 10
        if usados + coste > max_tokens and salida:
            omitidos.append(titulo)
            continue
        usados += coste
        salida.append(f"===== {titulo} =====\n{cuerpo}")
    salida += [f"OMITIDO (presupuesto): {t}" for t in omitidos]
    salida.append(f"~{usados} tokens de {max_tokens}")
    return 0, "\n\n".join(salida)


def cerrar(fid: str) -> Path:
    f, _ = _instruccion(fid)
    if f.status != "approved":
        raise ValueError(f"solo se cierra una instrucción approved (está en {f.status})")
    destino = fichas.cambiar_estado(PAQUETE, fid, "done")
    _campo(destino, "executed_at", reglas.ahora())
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap_ = sub.add_parser("aprobar")
    ap_.add_argument("id")
    ap_.add_argument("--humano", action="store_true")
    c = sub.add_parser("contexto")
    c.add_argument("id")
    c.add_argument("--max-tokens", type=int, default=None)
    sub.add_parser("cerrar").add_argument("id")
    sub.add_parser("pendientes")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "aprobar":
            print(aprobar(a.id, a.humano))
        elif a.cmd == "contexto":
            maximo = a.max_tokens or int(base.leer_ajustes(PAQUETE).get("max_tokens_contexto", 12000))
            codigo, texto = contexto(a.id, maximo)
            print(texto)
            return codigo
        elif a.cmd == "cerrar":
            print(cerrar(a.id))
        else:
            for f in fichas.listar(PAQUETE, "instruccion"):
                if f.status == "awaiting_approval":
                    print(f"{f.id}\t{f.titulo}")
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except (ValueError, PermissionError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
