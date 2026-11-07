#!/usr/bin/env python3
"""Comandos de paquetes de uxyngraphar (los expone `uxyngraphar.py`).

Catálogo (aquí se crean y editan los paquetes):
  catalogo                                   lista los paquetes del catálogo y si validan
  crear <id> --titulo "…" --familia <f> [--descripcion "…"] [--piezas a,b]  paquete nuevo: núcleo + piezas (NOMENCLATURA.md)
  validar [<id>…] [--completitud]            valida paquetes del catálogo; --completitud: piezas que tiene y que le faltan
  pieza <id> agregar|quitar <pieza>          añade una pieza estándar desde !base o la retira (y actualiza el manifiesto)
  indice-paquete [<id>…]                     regenera el bloque de entrada del README de cada paquete
  nomenclatura                               status heredados pendientes de pasar al vocabulario
  version <id> mayor|menor|parche            sube la versión en el catálogo
  construir <id>…|--todos --destino DIR      construye paquetes portátiles (con INTEGRIDAD.json)

Repo (RUTA = raíz de la app; por defecto, el directorio actual):
  instalar <id>… [--repo RUTA] [--base id]   instala en RUTA/uxyngraphar/paquetes/<id>/ (--base: se aplica en cada pedido)
  actualizar [<id>…] [--repo RUTA] [--forzar] actualiza o repara; nunca toca uxyngraphar/trabajo/
  quitar <id> [--repo RUTA] [--con-trabajo]  quita el paquete (y su trabajo solo si se pide)
  estado [--repo RUTA]                       instalados, versiones, integridad, actualizaciones
  verificar [--repo RUTA]                    ejecuta las verificaciones de cada paquete
  indice [--repo RUTA]                       regenera INDICE.md, el bloque de AGENTES.md y FLUJO.json si falta
  andamiar <id> [<variante> --nombre N] [--repo RUTA] [--aplicar]   andamiaje del paquete en el proyecto (simula; nunca sobrescribe)
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

import andamiaje  # noqa: E402
import catalogo  # noqa: E402
import nomenclatura  # noqa: E402
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


def cmd_andamiar(a) -> int:
    raiz = Path(a.repo).resolve()
    if not a.variante:
        for nombre, d in andamiaje.variantes(raiz, a.id).items():
            print(f"{nombre}\t{d['destino']}\t{d['descripcion']}")
        return 0
    if not a.nombre:
        print("error: falta --nombre", file=sys.stderr)
        return 1
    if not a.aplicar:
        for rel, existe in andamiaje.simular(raiz, a.id, a.variante, a.nombre):
            print(f"{'existe, se omitiría' if existe else 'crearía'}: {rel}")
        print("(simulación: añade --aplicar para crear)")
        return 0
    creados, omitidos = andamiaje.aplicar(raiz, a.id, a.variante, a.nombre)
    print("\n".join([*(f"creado: {r}" for r in creados), *(f"omitido (ya existe): {r}" for r in omitidos)]) or "(nada que crear)")
    return 0


def cmd_validar(a) -> int:
    filas = [m for m in catalogo.listar() if a.cmd == "catalogo" or not a.ids or m["id"] in a.ids]
    for m in filas:
        print(f"{m['id']}\t{m['version']}\t{m['titulo']}" + ("" if not m["errores"] else "\n  ERRORES: " + "; ".join(m["errores"]))
              + "".join(f"\n  aviso: {x}" for x in m.get("avisos", [])))
        if getattr(a, "completitud", False):
            c = catalogo.completitud(m["id"])
            print(f"  piezas: {', '.join(c['piezas']) or '(solo núcleo)'}"
                  + (f"\n  recomendadas que faltan: {', '.join(c['faltan_recomendadas'])}" if c["faltan_recomendadas"] else "")
                  + (f"\n  extensiones: {', '.join(c['extensiones'])}" if c["extensiones"] else ""))
    return 1 if any(m["errores"] for m in filas) else 0


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
    c.add_argument("--familia", required=True, choices=nomenclatura.NORMA["familias"])
    c.add_argument("--piezas", help=f"piezas estándar separadas por comas (por defecto: {','.join(catalogo.PIEZAS_AL_CREAR)})")
    sub.add_parser("nomenclatura")
    v = sub.add_parser("validar")
    v.add_argument("ids", nargs="*")
    v.add_argument("--completitud", action="store_true")
    pz = sub.add_parser("pieza")
    pz.add_argument("id")
    pz.add_argument("accion", choices=("agregar", "quitar"))
    pz.add_argument("pieza", choices=list(esp.base.PIEZAS))
    ip = sub.add_parser("indice-paquete")
    ip.add_argument("ids", nargs="*")
    ve = sub.add_parser("version")
    ve.add_argument("id")
    ve.add_argument("nivel", choices=catalogo.NIVELES)
    co = sub.add_parser("construir")
    co.add_argument("ids", nargs="*")
    co.add_argument("--todos", action="store_true")
    co.add_argument("--destino", required=True)
    an = sub.add_parser("andamiar")
    an.add_argument("id")
    an.add_argument("variante", nargs="?")
    an.add_argument("--nombre")
    an.add_argument("--repo", default=".")
    an.add_argument("--aplicar", action="store_true")
    for nombre in ("instalar", "actualizar", "quitar", "estado", "verificar", "indice", "flujo", "migrar"):
        s = sub.add_parser(nombre)
        s.add_argument("--repo", default=".")
        if nombre == "instalar":
            s.add_argument("ids", nargs="+")
            s.add_argument("--base", help="paquete base: FLUJO.json en trabajar_con con ese id")
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
            return cmd_validar(a)
        if a.cmd == "crear":
            print(catalogo.crear(a.id, a.titulo, a.descripcion, familia=a.familia, piezas=_lista(a.piezas)))
            print("Rellena los marcadores {{…}} de PAQUETE.md y de «alcance» en paquete.json; luego: uxyngraphar validar " + a.id)
        elif a.cmd == "pieza":
            hacer = catalogo.agregar_pieza if a.accion == "agregar" else catalogo.quitar_pieza
            errores = hacer(a.id, a.pieza)
            print(f"{a.id}: pieza «{a.pieza}» {'agregada' if a.accion == 'agregar' else 'quitada'}"
                  + "".join(f"\n  pendiente: {e}" for e in errores))
        elif a.cmd == "indice-paquete":
            for pid in a.ids or [m["id"] for m in catalogo.listar()]:
                print(f"{pid}: {'README actualizado' if catalogo.indice_paquete(pid) else 'al día'}")
        elif a.cmd == "nomenclatura":
            for m in catalogo.listar():
                for h in m["heredados"]:
                    print(f"{m['id']}: {h}")
        elif a.cmd == "version":
            print(catalogo.versionar(a.id, a.nivel))
        elif a.cmd == "construir":
            ids = [m["id"] for m in catalogo.listar()] if a.todos else a.ids
            for pid in ids:
                print(catalogo.construir(pid, Path(a.destino)))
        elif a.cmd == "instalar":
            print("instalados: " + ", ".join(repo.instalar(Path(a.repo), a.ids, paquete_base=a.base))
                  + (f" · paquete base: {a.base}" if a.base else ""))
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
            return {"estado": cmd_estado, "verificar": cmd_verificar, "flujo": cmd_flujo, "andamiar": cmd_andamiar,
                    "migrar": cmd_migrar, "panel": cmd_panel}[a.cmd](a)
    except (ValueError, FileNotFoundError, FileExistsError, repo.InstalacionAntigua) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
