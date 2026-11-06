#!/usr/bin/env python3
"""Comandos de paquetes de uxyngraphar (los expone `uxyngraphar.py`).

Catálogo (aquí se crean y editan los paquetes):
  catalogo                                   lista los paquetes del catálogo y si validan
  crear <id> --titulo "…" [--descripcion "…"] esqueleto de un paquete nuevo
  validar [<id>…]                            valida paquetes del catálogo
  version <id> mayor|menor|parche            sube la versión en el catálogo
  construir <id>…|--todos --destino DIR      construye paquetes portátiles (con INTEGRIDAD.json)

Repo (RUTA = raíz de la app; por defecto, el directorio actual):
  instalar <id>… [--repo RUTA]               instala en RUTA/uxyngraphar/paquetes/<id>/
  actualizar [<id>…] [--repo RUTA] [--forzar] actualiza o repara; nunca toca uxyngraphar/trabajo/
  quitar <id> [--repo RUTA] [--con-trabajo]  quita el paquete (y su trabajo solo si se pide)
  estado [--repo RUTA]                       instalados, versiones, integridad, actualizaciones
  verificar [--repo RUTA]                    ejecuta las verificaciones de cada paquete
  indice [--repo RUTA]                       regenera INDICE.md, el bloque de AGENTES.md y FLUJO.json si falta
  flujo [--repo RUTA] [--modo M] [--leer a,b] [--trabajar-con id|-] [--secuencia a,b]   ver o cambiar FLUJO.json (persona)
  migrar [--repo RUTA] [--aplicar]           migra instalaciones 1.x (por defecto solo simula)
  panel [--puerto N] [--no-abrir]            panel del navegador
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import catalogo  # noqa: E402
import especificacion as esp  # noqa: E402
import generar  # noqa: E402
import repo  # noqa: E402


def _lista(texto: str | None) -> list[str] | None:
    return None if texto is None else [x.strip() for x in texto.split(",") if x.strip()]


def cmd_flujo(a) -> int:
    raiz = Path(a.repo).resolve()
    generar.flujo_inicial(raiz)
    flujo = generar.leer_flujo(raiz)
    cambios = {"modo": a.modo, "leer_por_defecto": _lista(a.leer), "secuencia": _lista(a.secuencia)}
    if a.trabajar_con is not None:
        cambios["trabajar_con"] = None if a.trabajar_con == "-" else a.trabajar_con
    cambios = {k: v for k, v in cambios.items() if v is not None}
    if cambios:
        errores = generar.guardar_flujo(raiz, {**flujo, **cambios})
        if errores:
            print("FLUJO.json no cambió:\n  " + "\n  ".join(errores), file=sys.stderr)
            return 1
        flujo = generar.leer_flujo(raiz)
    print(json.dumps(flujo, ensure_ascii=False, indent=2))
    return 0


def cmd_estado(a) -> int:
    filas = repo.estado(Path(a.repo).resolve())
    if not filas:
        print("(sin paquetes instalados)")
    for e in filas:
        marca = "íntegro" if e["integro"] else "ALTERADO"
        extra = f" → {e['catalogo']} disponible" if e["actualizable"] else ""
        print(f"{e['id']}\t{e['version']}\t{marca}{extra}")
    return 0


def cmd_verificar(a) -> int:
    codigo = 0
    for r in repo.verificar(Path(a.repo).resolve()):
        print(f"[{'ok' if r['codigo'] == 0 else 'FALLA'}] {r['paquete']} · {r['verificacion']}\n{r['salida']}\n")
        codigo = codigo or (1 if r["codigo"] else 0)
    return codigo


def cmd_migrar(a) -> int:
    from migracion import migrar
    return migrar.main(a.repo, aplicar=a.aplicar)


def cmd_panel(a) -> int:
    import panel
    return panel.servir(a.puerto, abrir=not a.no_abrir)


def analizador() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="uxyngraphar", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalogo")
    c = sub.add_parser("crear")
    c.add_argument("id")
    c.add_argument("--titulo", required=True)
    c.add_argument("--descripcion", default="")
    v = sub.add_parser("validar")
    v.add_argument("ids", nargs="*")
    ve = sub.add_parser("version")
    ve.add_argument("id")
    ve.add_argument("nivel", choices=catalogo.NIVELES)
    co = sub.add_parser("construir")
    co.add_argument("ids", nargs="*")
    co.add_argument("--todos", action="store_true")
    co.add_argument("--destino", required=True)
    for nombre in ("instalar", "actualizar", "quitar", "estado", "verificar", "indice", "flujo", "migrar"):
        s = sub.add_parser(nombre)
        s.add_argument("--repo", default=".")
        if nombre == "instalar":
            s.add_argument("ids", nargs="+")
        elif nombre == "actualizar":
            s.add_argument("ids", nargs="*")
            s.add_argument("--forzar", action="store_true")
        elif nombre == "quitar":
            s.add_argument("id")
            s.add_argument("--con-trabajo", action="store_true")
        elif nombre == "flujo":
            s.add_argument("--modo", choices=esp.MODOS)
            s.add_argument("--leer")
            s.add_argument("--trabajar-con")
            s.add_argument("--secuencia")
        elif nombre == "migrar":
            s.add_argument("--aplicar", action="store_true")
    pa = sub.add_parser("panel")
    pa.add_argument("--puerto", type=int, default=0)
    pa.add_argument("--no-abrir", "--fondo", dest="no_abrir", action="store_true")
    pa.add_argument("--bienvenida", action="store_true", help=argparse.SUPPRESS)
    return p


def main(argv: list[str] | None = None) -> int:
    a = analizador().parse_args(argv)
    try:
        if a.cmd == "catalogo" or a.cmd == "validar":
            filas = [m for m in catalogo.listar() if a.cmd == "catalogo" or not a.ids or m["id"] in a.ids]
            for m in filas:
                print(f"{m['id']}\t{m['version']}\t{m['titulo']}" + ("" if not m["errores"] else "\n  ERRORES: " + "; ".join(m["errores"])))
            return 1 if any(m["errores"] for m in filas) else 0
        if a.cmd == "crear":
            print(catalogo.crear(a.id, a.titulo, a.descripcion))
        elif a.cmd == "version":
            print(catalogo.versionar(a.id, a.nivel))
        elif a.cmd == "construir":
            ids = [m["id"] for m in catalogo.listar()] if a.todos else a.ids
            for pid in ids:
                print(catalogo.construir(pid, Path(a.destino)))
        elif a.cmd == "instalar":
            print("instalados: " + ", ".join(repo.instalar(Path(a.repo), a.ids)))
        elif a.cmd == "actualizar":
            hechos = repo.actualizar(Path(a.repo), a.ids or None, forzar=a.forzar)
            print("actualizados: " + (", ".join(hechos) or "(nada que actualizar)"))
        elif a.cmd == "quitar":
            repo.quitar(Path(a.repo), a.id, a.con_trabajo)
            print(f"quitado: {a.id}" + (" (con su trabajo)" if a.con_trabajo else " (su trabajo sigue en uxyngraphar/trabajo/)"))
        elif a.cmd == "indice":
            generar.regenerar(Path(a.repo).resolve())
            print(generar.indice(Path(a.repo).resolve()))
        else:
            return {"estado": cmd_estado, "verificar": cmd_verificar, "flujo": cmd_flujo,
                    "migrar": cmd_migrar, "panel": cmd_panel}[a.cmd](a)
    except (ValueError, FileNotFoundError, FileExistsError, repo.InstalacionAntigua) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
