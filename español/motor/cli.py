#!/usr/bin/env python3
"""Comandos de sistemas de uxyngraphar (los expone `uxyngraphar.py`).

Catálogo (aquí se crean y editan los sistemas):
  catalogo                                   lista los sistemas del catálogo y si validan
  crear <id> --titulo "…" --familia <f> [--descripcion "…"] [--piezas a,b] [--json]  sistema nuevo: núcleo + piezas (NOMENCLATURA.md)
  generar plantilla [--id X] [--familia F]   especificación JSON de partida para un sistema completo (GENERADOR.md)
  generar desde <spec.json|-> [--aplicar] [--json]   sistema completo desde la especificación (por defecto simula)
  generar pendientes <id> [--json]           qué le falta a un sistema (archivo:línea) y la siguiente acción
  validar [<id>…] [--completitud] [--json]   valida sistemas del catálogo; --completitud: piezas que tiene y que le faltan
  pieza <id> agregar|quitar <pieza>          añade una pieza estándar desde _base o la retira (y actualiza el manifiesto)
  indice-sistema [<id>…]                     regenera el bloque de entrada del README de cada sistema
  nomenclatura                               status heredados del catálogo pendientes de pasar al vocabulario
  nomenclatura migrar [--repo RUTA] [--aplicar]   fichas de un proyecto al vocabulario de NOMENCLATURA.md (por defecto simula)
  version <id> mayor|menor|parche            sube la versión en el catálogo
  construir <id>…|--todos --destino DIR      construye sistemas portátiles (con scripts/comun de _base e INTEGRIDAD.json)
  sincronizar-comun                          copia scripts/comun de _base en cada sistema (copias locales, no versionadas)
  empaquetar <id>…|--todos --destino DIR     artefacto de cada sistema (<id>-<version>.zip reproducible, el que se publica)

Servidor de sistemas de gobernanza (el instalador llega vacío: los sistemas se buscan y se traen de aquí):
  buscar [TEXTO] [--familia F] [--json]      busca en el servidor (sin red, en el último índice guardado)
  info <[editor/]id[@X.Y.Z]> [--json]        ficha de un sistema del servidor y sus versiones
  traer <[editor/]id[@X.Y.Z]>…               lo descarga a la caché local (luego «instalar» lo usa sin red)
  publicar <id>…|--todos [--simular]         sube la versión del catálogo local al servidor (necesita token)
  sesion guardar <token>|borrar|ver          token de publicación (o la variable UXYNGRAPHAR_TOKEN)
  cache [limpiar]                            sistemas traídos y el índice guardado

Repo (RUTA = raíz de la app; por defecto, el directorio actual):
  instalar <id>… [--repo RUTA] [--base id]   instala en RUTA/uxyngraphar/sistemas-de-gobernanza/<id>/ (--base: se aplica en cada pedido)
  actualizar [<id>…] [--repo RUTA] [--forzar] actualiza o repara; nunca toca uxyngraphar/trabajo/
  quitar <id> [--repo RUTA] [--con-trabajo]  quita el sistema (y su trabajo solo si se pide)
  estado [--repo RUTA]                       instalados, versiones, integridad, actualizaciones
  verificar [--repo RUTA] [--segundos N] [--formato texto|json] [--trabajos N]   verificaciones de cada sistema
                                             (0 bien, 1 problemas, 2 error de ejecución; límite por defecto: 300 s)
  indice [--repo RUTA]                       regenera INDICE.md, el bloque de AGENTES.md y FLUJO.json si falta
  andamiar <id> [<variante> --nombre N] [--repo RUTA] [--aplicar]   andamiaje del sistema en el proyecto (simula; nunca sobrescribe)
  flujo [--repo RUTA] [--modo M] [--leer a,b] [--trabajar-con id|-] [--secuencia a,b]   ver o cambiar FLUJO.json (persona)
  grupos [guardar NOMBRE RUTA…|borrar NOMBRE|actualizar NOMBRE|verificar NOMBRE|matriz NOMBRE|aplicar-flujo NOMBRE ID]
                                             repos que forman un sistema y se gestionan a la vez
  completado bash|zsh|fish|powershell        script de autocompletado (añádelo al perfil de tu shell)
  diagnostico [--json] [--anonimizar] [--sin-red]   informe del equipo y de los proyectos (para entender o pegar en una incidencia)
  integracion [agregar|quitar workflow|precommit] [--repo RUTA]   workflow de CI y gancho pre-commit de «verificar» (opcionales)
  deshacer [--repo RUTA] [--lista] [--respaldo NOMBRE]   devuelve el proyecto a antes del último cambio (o del elegido)
  retirar [--repo RUTA] [--con-trabajo]      quita uxyngraphar del proyecto (el trabajo propio se conserva)

Este equipo:
  proyectos [agregar RUTA…|quitar RUTA|buscar RUTA]   proyectos que gestiona el panel
  flujos-guardados [guardar NOMBRE --repo RUTA|aplicar ID RUTA…|borrar ID|exportar ID|importar ARCHIVO]   flujos reutilizables
  accesos [menu,escritorio,barra|--quitar]   accesos directos al panel (sin argumentos: los disponibles)
  panel [--puerto N] [--no-abrir] [--mantener] [--primer-plano] [--cerrar]   panel del navegador, independiente de la terminal
                                             (se cierra solo sin pestañas abiertas; --cerrar lo cierra)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import andamiaje  # noqa: E402
import catalogo  # noqa: E402
import remoto  # noqa: E402
import generador  # noqa: E402
import nomenclatura  # noqa: E402
import especificacion as esp  # noqa: E402
import generar  # noqa: E402
import repo  # noqa: E402
import transaccion  # noqa: E402


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
        print("(sin sistemas instalados)")
    for e in filas:
        marca = "íntegro" if e["integro"] else "ALTERADO"
        extra = f" → {e['catalogo']} disponible" if e["actualizable"] else ""
        print(f"{e['id']}\t{e['version']}\t{marca}{extra}")
    return 0


def cmd_verificar(a) -> int:
    raiz = Path(a.repo).resolve()
    resultados = repo.verificar(raiz, a.segundos, max(1, a.trabajos))
    codigo = repo.codigo_verificacion(resultados)
    if a.formato == "json":   # formato estable: ESPECIFICACION.md, «verificar --formato json»
        _json({"formato": 1, "repo": str(raiz), "codigo": codigo, "resultados": resultados})
        return codigo
    for r in resultados:
        print(f"[{'ok' if r['codigo'] == 0 else 'FALLA'}] {r['sistema']} · {r['verificacion']}\n{r['salida']}\n")
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


def _json(datos) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2))


def _imprimir_pendientes(p: dict) -> None:
    print(f"{p['id']}: {'listo' if p['listo'] else 'pendiente'}")
    for e in p["errores"]:
        print(f"  error: {e}")
    for x in p["marcadores"]:
        print(f"  rellenar {x['archivo']}:{x['linea']}  {x['marcador']}")
    for pieza in p["faltan_recomendadas"]:
        print(f"  pieza recomendada: {pieza}")
    for aviso in p["avisos"]:
        print(f"  aviso: {aviso}")
    print(f"siguiente: {p['siguiente']}")


def cmd_generar(a) -> int:
    if a.accion == "plantilla":
        _json(generador.plantilla_spec(a.id, a.familia))
        return 0
    if a.accion == "pendientes":
        p = generador.pendientes(a.id)
        _json(p) if a.json else _imprimir_pendientes(p)
        return 0 if p["listo"] else 1
    texto = sys.stdin.read() if a.spec == "-" else Path(a.spec).read_text(encoding="utf-8")
    try:
        spec = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"la especificación no es JSON válido: {e}") from e
    r = generador.desde_spec(spec, aplicar=a.aplicar)
    if a.json:
        _json(r)
    else:
        for e in r["errores"]:
            print(f"error: {e}")
        for aviso in r["avisos"]:
            print(f"aviso: {aviso}")
        if r["errores"]:
            print("No se generó nada: corrige la especificación y vuelve a ejecutar.")
        elif r["aplicado"]:
            print(f"creado: {r['ruta']}\nsiguiente: uxyngraphar generar pendientes {r['id']}")
        else:
            print("\n".join(f"crearía: {r['id']}/{x}" for x in r["archivos"]))
            print("(simulación: añade --aplicar para crearlo)")
    return 1 if r["errores"] else 0


def cmd_validar(a) -> int:
    filas = [m for m in catalogo.listar() if a.cmd == "catalogo" or not a.ids or m["id"] in a.ids]
    if getattr(a, "json", False):
        _json([{"id": m["id"], "version": m["version"], "titulo": m["titulo"], "errores": m["errores"], "avisos": m.get("avisos", []),
                **({"completitud": catalogo.completitud(m["id"])} if a.completitud else {})} for m in filas])
        return 1 if any(m["errores"] for m in filas) else 0
    for m in filas:
        print(f"{m['id']}\t{m['version']}\t{m['titulo']}" + ("" if not m["errores"] else "\n  ERRORES: " + "; ".join(m["errores"]))
              + "".join(f"\n  aviso: {x}" for x in m.get("avisos", [])))
        if getattr(a, "completitud", False):
            c = catalogo.completitud(m["id"])
            print(f"  piezas: {', '.join(c['piezas']) or '(solo núcleo)'}"
                  + (f"\n  recomendadas que faltan: {', '.join(c['faltan_recomendadas'])}" if c["faltan_recomendadas"] else "")
                  + (f"\n  extensiones: {', '.join(c['extensiones'])}" if c["extensiones"] else ""))
    return 1 if any(m["errores"] for m in filas) else 0


def cmd_grupos(a) -> int:
    import grupos
    if a.accion and not a.args:
        raise ValueError(f"grupos {a.accion}: falta el nombre del grupo")
    if a.accion == "guardar":
        print("\n".join(f"{a.args[0]}: {r}" for r in grupos.guardar(a.args[0], a.args[1:])))
        return 0
    if a.accion == "borrar":
        grupos.borrar(a.args[0])
        print(f"grupo borrado: {a.args[0]}")
        return 0
    if a.accion == "matriz":
        m = grupos.matriz(a.args[0])
        if a.json:
            _json(m)
            return 0
        print("sistema\t" + "\t".join(r["nombre"] for r in m["repos"]))
        for pid in m["sistemas"]:
            celdas = [r["sistemas"].get(pid) for r in m["repos"]]
            print(pid + "\t" + "\t".join("—" if not c else c["version"] + ("" if c["integro"] else "!") + ("↑" if c["actualizable"] else "") for c in celdas))
        return 0
    if a.accion in ("actualizar", "verificar", "aplicar-flujo"):
        if a.accion == "aplicar-flujo" and len(a.args) < 2:
            raise ValueError("grupos aplicar-flujo NOMBRE ID")
        filas = (grupos.actualizar(a.args[0]) if a.accion == "actualizar" else grupos.verificar(a.args[0]) if a.accion == "verificar"
                 else grupos.aplicar_flujo(a.args[0], a.args[1]))
        if a.json:
            _json(filas)
        for f in filas if not a.json else []:
            detalle = f.get("error") or (", ".join(f.get("actualizados", [])) or "al día") if a.accion == "actualizar" else \
                f.get("error") or (("con problemas" if f.get("codigo") else "bien") + (f" · contratos {f['contratos']}" if f.get("contratos") else ""))
            print(f"{f.get('nombre') or Path(f['ruta']).name}: {detalle}")
        return 1 if any(f.get("error") or f.get("codigo") for f in filas) else 0
    for nombre, rutas in grupos.listar().items():
        print(f"{nombre}\t" + ", ".join(Path(r).name for r in rutas))
    return 0


def cmd_vocabulario(a) -> int:
    import vocabulario
    raiz = Path(a.repo).resolve()
    if not a.aplicar:
        cambios = vocabulario.plan(raiz)
        for c in cambios:
            movida = f" → {c['destino']}" if c["destino"] != c["origen"] else ""
            print(f"{c['sistema']}: {c['ficha']} «{c['antes']}» → «{c['despues']}»{movida}")
        print(f"{len(cambios)} fichas por migrar" + ("\n(simulación: añade --aplicar)" if cambios else " (todo está en el vocabulario nuevo)"))
        return 0
    r = vocabulario.aplicar(raiz)
    print(f"{len(r['cambios'])} fichas migradas" + (f"; respaldo en {r['respaldo']}" if r["respaldo"] else ""))
    return 0


def cmd_proyectos(a) -> int:
    import proyectos
    if a.accion == "agregar":
        print("\n".join(f"añadido: {r}" for r in proyectos.agregar(a.rutas)))
    elif a.accion == "quitar":
        for r in a.rutas:
            proyectos.quitar(str(Path(r).expanduser().resolve()))
            print(f"quitado de la lista: {r}")
    elif a.accion == "buscar":
        for p in proyectos.buscar(a.rutas[0] if a.rutas else "."):
            print(f"{p['ruta']}" + (" (ya en la lista)" if p["registrado"] else ""))
    else:
        for p in proyectos.resumenes():
            marca = "NO EXISTE" if not p["existe"] else \
                f"{len(p['sistemas'])} sistemas" + (f", {p['actualizables']} por actualizar" if p["actualizables"] else "") + \
                (f", {p['alterados']} alterados" if p["alterados"] else "")
            print(f"{p['ruta']}\t{marca}")
    return 0


def cmd_flujos_guardados(a) -> int:
    import flujos_guardados as guardados
    necesarios = {"guardar": "NOMBRE", "aplicar": "ID", "borrar": "ID", "exportar": "ID", "importar": "ARCHIVO"}
    if a.accion in necesarios and not a.args:
        raise ValueError(f"flujos-guardados {a.accion}: falta {necesarios[a.accion]}")
    if a.accion == "guardar":
        print(guardados.desde_proyecto(Path(a.repo).resolve(), " ".join(a.args), a.descripcion))
    elif a.accion == "aplicar":
        codigo = 0
        for r in guardados.aplicar(a.args[0], a.args[1:] or [a.repo]):
            print(f"{r['ruta']}: " + (f"ERROR {r['error']}" if r["error"] else f"aplicado; instalados: {', '.join(r['instalados']) or '(ninguno)'}"))
            codigo = codigo or (1 if r["error"] else 0)
        return codigo
    elif a.accion == "borrar":
        guardados.borrar(a.args[0])
        print(f"borrado: {a.args[0]}")
    elif a.accion == "exportar":
        print(json.dumps(guardados.exportar(a.args[0]), ensure_ascii=False, indent=2))
    elif a.accion == "importar":
        print(guardados.importar(json.loads(Path(a.args[0]).read_text(encoding="utf-8"))))
    else:
        for g in guardados.listar():
            print(f"{g['id']}\t{g.get('nombre', '')}\t{g.get('flujo', {}).get('modo', '')}\t{', '.join(g.get('sistemas', []))}")
    return 0


def cmd_accesos(a) -> int:
    import herramienta
    if a.quitar or a.tipos is not None:
        tipos = [] if a.quitar else (_lista(a.tipos) or [])
        r = herramienta.cambiar_accesos(tipos)
        print("\n".join(r["avisos"]) or "accesos directos actualizados")
    else:
        r = herramienta.accesos()
    for d in r["disponibles"]:
        print(f"{d['tipo']}\t{'creado' if d['creado'] else '-'}\t{d['etiqueta']}" + (f"  ({d['nota']})" if not d["posible"] else ""))
    return 0


def cmd_panel(a) -> int:
    import panel
    if a.cerrar:
        abierto = panel.cerrar_abierto()
        print(f"Panel cerrado (puerto {abierto['puerto']})." if abierto else "No hay ningún panel abierto.")
        return 0
    arrancar = panel.servir if a.primer_plano else panel.lanzar
    return arrancar(a.puerto, abrir=not a.no_abrir, bienvenida=a.bienvenida, mantener=a.mantener)


def analizador() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="uxyngraphar", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalogo")
    sub.add_parser("sincronizar-comun")
    c = sub.add_parser("crear")
    c.add_argument("id")
    c.add_argument("--titulo", required=True)
    c.add_argument("--descripcion", default="")
    c.add_argument("--familia", required=True, choices=nomenclatura.NORMA["familias"])
    c.add_argument("--piezas", help=f"piezas estándar separadas por comas (por defecto: {','.join(catalogo.PIEZAS_AL_CREAR)})")
    c.add_argument("--json", action="store_true", help="ruta y pendientes en JSON")
    g = sub.add_parser("generar")
    gs = g.add_subparsers(dest="accion", required=True)
    gp = gs.add_parser("plantilla")
    gp.add_argument("--id", default="contratos-de-pago")
    gp.add_argument("--familia", default="proceso", choices=nomenclatura.NORMA["familias"])
    gd = gs.add_parser("desde")
    gd.add_argument("spec", help="archivo JSON de especificación, o «-» para leerla de la entrada estándar")
    gd.add_argument("--aplicar", action="store_true")
    gd.add_argument("--json", action="store_true")
    gq = gs.add_parser("pendientes")
    gq.add_argument("id")
    gq.add_argument("--json", action="store_true")
    no = sub.add_parser("nomenclatura")
    no.add_argument("accion", nargs="?", choices=("migrar",))
    no.add_argument("--repo", default=".")
    no.add_argument("--aplicar", action="store_true")
    v = sub.add_parser("validar")
    v.add_argument("ids", nargs="*")
    v.add_argument("--completitud", action="store_true")
    v.add_argument("--json", action="store_true")
    pz = sub.add_parser("pieza")
    pz.add_argument("id")
    pz.add_argument("accion", choices=("agregar", "quitar"))
    pz.add_argument("pieza", choices=list(esp.base.PIEZAS))
    ip = sub.add_parser("indice-sistema")
    ip.add_argument("ids", nargs="*")
    ve = sub.add_parser("version")
    ve.add_argument("id")
    ve.add_argument("nivel", choices=catalogo.NIVELES)
    co = sub.add_parser("construir")
    co.add_argument("ids", nargs="*")
    co.add_argument("--todos", action="store_true")
    co.add_argument("--destino", required=True)
    em = sub.add_parser("empaquetar")
    em.add_argument("ids", nargs="*")
    em.add_argument("--todos", action="store_true")
    em.add_argument("--destino", required=True)
    bu = sub.add_parser("buscar")
    bu.add_argument("texto", nargs="*")
    bu.add_argument("--familia", default="")
    bu.add_argument("--json", action="store_true")
    inf = sub.add_parser("info")
    inf.add_argument("ref")
    inf.add_argument("--json", action="store_true")
    tr = sub.add_parser("traer")
    tr.add_argument("refs", nargs="+")
    pu = sub.add_parser("publicar")
    pu.add_argument("ids", nargs="*")
    pu.add_argument("--todos", action="store_true")
    pu.add_argument("--simular", action="store_true")
    se = sub.add_parser("sesion")
    se.add_argument("accion", choices=("guardar", "borrar", "ver"))
    se.add_argument("token", nargs="?")
    ca = sub.add_parser("cache")
    ca.add_argument("accion", nargs="?", choices=("limpiar",))
    an = sub.add_parser("andamiar")
    an.add_argument("id")
    an.add_argument("variante", nargs="?")
    an.add_argument("--nombre")
    an.add_argument("--repo", default=".")
    an.add_argument("--aplicar", action="store_true")
    pr = sub.add_parser("proyectos")
    pr.add_argument("accion", nargs="?", choices=("agregar", "quitar", "buscar"))
    pr.add_argument("rutas", nargs="*")
    fg = sub.add_parser("flujos-guardados")
    fg.add_argument("accion", nargs="?", choices=("guardar", "aplicar", "borrar", "exportar", "importar"))
    fg.add_argument("args", nargs="*")
    fg.add_argument("--repo", default=".")
    fg.add_argument("--descripcion", default="")
    ac = sub.add_parser("accesos")
    ac.add_argument("tipos", nargs="?")
    ac.add_argument("--quitar", action="store_true")
    gr = sub.add_parser("grupos")
    gr.add_argument("accion", nargs="?", choices=("guardar", "borrar", "actualizar", "verificar", "matriz", "aplicar-flujo"))
    gr.add_argument("args", nargs="*")
    gr.add_argument("--json", action="store_true")
    cp = sub.add_parser("completado")
    cp.add_argument("shell", choices=("bash", "zsh", "fish", "powershell"))
    dg = sub.add_parser("diagnostico")
    dg.add_argument("--json", action="store_true")
    dg.add_argument("--anonimizar", action="store_true", help="la carpeta personal pasa a ~ y los proyectos se nombran por su carpeta")
    dg.add_argument("--sin-red", action="store_true", help="no consultar la última versión publicada")
    it = sub.add_parser("integracion")
    it.add_argument("accion", nargs="?", choices=("agregar", "quitar"))
    it.add_argument("tipo", nargs="?", choices=("workflow", "precommit"))
    it.add_argument("--repo", default=".")
    for nombre in ("instalar", "actualizar", "quitar", "estado", "verificar", "indice", "flujo", "retirar", "deshacer"):
        s = sub.add_parser(nombre)
        s.add_argument("--repo", default=".")
        if nombre == "instalar":
            s.add_argument("ids", nargs="+")
            s.add_argument("--base", help="sistema base: FLUJO.json en trabajar_con con ese id")
        elif nombre == "actualizar":
            s.add_argument("ids", nargs="*")
            s.add_argument("--forzar", action="store_true")
        elif nombre == "quitar":
            s.add_argument("id")
            s.add_argument("--con-trabajo", action="store_true")
        elif nombre == "retirar":
            s.add_argument("--con-trabajo", action="store_true")
        elif nombre == "flujo":
            s.add_argument("--modo", choices=esp.MODOS)
            s.add_argument("--leer")
            s.add_argument("--trabajar-con")
            s.add_argument("--secuencia")
        elif nombre == "deshacer":
            s.add_argument("--lista", action="store_true", help="solo lista los cambios que se pueden deshacer")
            s.add_argument("--respaldo", help="nombre del respaldo (de --lista); por defecto, el último cambio")
        elif nombre == "verificar":
            s.add_argument("--segundos", type=float, default=repo.SEGUNDOS_VERIFICAR,
                           help=f"límite por verificación (por defecto {repo.SEGUNDOS_VERIFICAR}); si se agota, código 124")
            s.add_argument("--formato", choices=("texto", "json"), default="texto",
                           help="json: salida estable para CI (salida: 0 bien, 1 problemas, 2 error de ejecución)")
            s.add_argument("--trabajos", type=int, default=1, help="verificaciones a la vez (por defecto 1)")
    pa = sub.add_parser("panel")
    pa.add_argument("--puerto", type=int, default=0)
    pa.add_argument("--no-abrir", "--fondo", dest="no_abrir", action="store_true")
    pa.add_argument("--bienvenida", action="store_true", help=argparse.SUPPRESS)
    pa.add_argument("--mantener", action="store_true", help="no cerrarlo solo aunque no quede ninguna pestaña abierta")
    pa.add_argument("--primer-plano", action="store_true", help="atado a esta terminal (Ctrl+C lo cierra), con su registro a la vista")
    pa.add_argument("--cerrar", action="store_true", help="cierra el panel abierto en este equipo")
    return p


def cmd_servidor(a) -> int:
    import artefacto
    import remoto
    if a.cmd == "empaquetar":
        for pid in ([m["id"] for m in catalogo.listar()] if a.todos else a.ids):
            z = artefacto.empaquetar(pid, Path(a.destino))
            print(f"{z}  sha256 {artefacto.sha256_de(z)}")
    elif a.cmd == "buscar":
        hallados = remoto.buscar(" ".join(a.texto), a.familia)
        if a.json:
            _json(hallados)
        for s in [] if a.json else hallados:
            ultima = (s.get("versiones") or [{}])[0].get("version", s.get("version", ""))
            print(f"{s.get('editor', '')}/{s['id']}  {ultima}  {s.get('titulo', '')}")
        if not hallados and not a.json:
            print("sin resultados")
    elif a.cmd == "info":
        f = remoto.ficha(a.ref)
        if a.json:
            _json(f)
        else:
            print(f"{f['editor']}/{f['id']} — {f.get('titulo', '')}\n{f.get('descripcion', '')}")
            for v in f.get("versiones", []):
                print(f"  {v['version']}  motor {v.get('motor', '')}" + ("  (retirada)" if v.get("retirada") else ""))
            print(f"para instalar: uxyngraphar instalar {f['id']}")
    elif a.cmd == "traer":
        for ref in a.refs:
            print(remoto.traer(ref))
    elif a.cmd == "publicar":
        import tempfile
        ids = [m["id"] for m in catalogo.listar() if not m["errores"]] if a.todos else a.ids
        if not ids:
            raise ValueError("indica ids o --todos")
        with tempfile.TemporaryDirectory(prefix="uxy-publicar-") as tmp:
            for pid in ids:
                z = artefacto.empaquetar(pid, Path(tmp))
                if a.simular:
                    print(f"{pid}: {z.name} listo ({z.stat().st_size} bytes, sha256 {artefacto.sha256_de(z)}); no se subió (--simular)")
                    continue
                r = remoto.publicar(z)
                print(f"{pid}: publicado {r.get('editor', '')}/{r.get('id', pid)}@{r.get('version', '')}")
    elif a.cmd == "sesion":
        if a.accion == "guardar":
            if not a.token:
                raise ValueError("uso: uxyngraphar sesion guardar <token>")
            print(f"token guardado en {remoto.guardar_token(a.token)}")
        elif a.accion == "borrar":
            print("token borrado" if remoto.borrar_token() else "no había token guardado")
        else:
            print(f"servidor: {remoto.servidor() or '(sin red)'}\ntoken: {'sí' if remoto.token() else 'no'}")
    elif a.cmd == "cache":
        if a.accion == "limpiar":
            print(f"caché vaciada ({remoto.limpiar_cache()} versiones)")
        else:
            c = remoto.cache()
            for marca in sorted(c.glob(f"*/*/*/{remoto.MARCA_COMPLETO}")) if c.is_dir() else []:
                editor, pid, version = marca.parent.relative_to(c).parts
                print(f"{editor}/{pid}@{version}")
            print(f"carpeta: {c}")
    return 0


CAMBIAN = {"instalar", "actualizar", "quitar", "retirar", "deshacer", "indice"}


def main(argv: list[str] | None = None) -> int:
    a = analizador().parse_args(argv)
    accion = ("nomenclatura migrar" if a.cmd == "nomenclatura" and getattr(a, "accion", None) == "migrar" and a.aplicar
              else "flujo" if a.cmd == "flujo" and (a.modo or a.leer or a.secuencia or a.trabajar_con)
              else a.cmd if a.cmd in CAMBIAN else "")
    if not accion:
        return _main(a)
    import auditoria
    proyecto = str(Path(a.repo).resolve()) if getattr(a, "repo", None) else ""
    ids = list(getattr(a, "ids", None) or ([a.id] if getattr(a, "id", None) else []))
    try:
        codigo = _main(a)
    except BaseException as e:
        auditoria.registrar(accion, proyecto, ids, error=f"{type(e).__name__}: {e}")
        raise
    auditoria.registrar(accion, proyecto, ids, error="" if codigo == 0 else f"código {codigo}")
    return codigo


def _main(a) -> int:
    try:
        if a.cmd in ("catalogo", "validar"):
            return cmd_validar(a)
        if a.cmd == "crear":
            ruta = catalogo.crear(a.id, a.titulo, a.descripcion, familia=a.familia, piezas=_lista(a.piezas))
            if a.json:
                _json({"ruta": str(ruta), "pendientes": generador.pendientes(a.id)})
            else:
                print(ruta)
                print(f"Rellena los marcadores {{{{…}}}}; «uxyngraphar generar pendientes {a.id}» dice dónde y qué sigue.")
        elif a.cmd == "pieza":
            hacer = catalogo.agregar_pieza if a.accion == "agregar" else catalogo.quitar_pieza
            errores = hacer(a.id, a.pieza)
            print(f"{a.id}: pieza «{a.pieza}» {'agregada' if a.accion == 'agregar' else 'quitada'}"
                  + "".join(f"\n  pendiente: {e}" for e in errores))
        elif a.cmd == "indice-sistema":
            for pid in a.ids or [m["id"] for m in catalogo.listar()]:
                print(f"{pid}: {'README actualizado' if catalogo.indice_sistema(pid) else 'al día'}")
        elif a.cmd == "nomenclatura" and a.accion == "migrar":
            return cmd_vocabulario(a)
        elif a.cmd == "nomenclatura":
            for m in catalogo.listar():
                for h in m["heredados"]:
                    print(f"{m['id']}: {h}")
        elif a.cmd == "sincronizar-comun":
            cambiados = catalogo.sincronizar_comun()
            print(("scripts/comun al día en: " + ", ".join(cambiados)) if cambiados else "todas las copias de scripts/comun estaban al día")
        elif a.cmd == "version":
            print(catalogo.versionar(a.id, a.nivel))
        elif a.cmd == "construir":
            ids = [m["id"] for m in catalogo.listar()] if a.todos else a.ids
            for pid in ids:
                print(catalogo.construir(pid, Path(a.destino)))
        elif a.cmd in ("empaquetar", "buscar", "info", "traer", "publicar", "sesion", "cache"):
            return cmd_servidor(a)
        elif a.cmd == "instalar":
            print("instalados: " + ", ".join(repo.instalar(Path(a.repo), a.ids, sistema_base=a.base))
                  + (f" · sistema base: {a.base}" if a.base else ""))
        elif a.cmd == "actualizar":
            hechos = repo.actualizar(Path(a.repo), a.ids or None, forzar=a.forzar)
            print("actualizados: " + (", ".join(hechos) or "(nada que actualizar)"))
            import vocabulario
            pendientes = vocabulario.pendientes(Path(a.repo).resolve())
            if pendientes:
                print(f"aviso: {pendientes} fichas usan status que los sistemas ya no tienen; para pasarlas al vocabulario nuevo:\n"
                      f"  uxyngraphar nomenclatura migrar --repo {Path(a.repo).resolve()}   (simula; añade --aplicar)")
        elif a.cmd == "quitar":
            repo.quitar(Path(a.repo), a.id, a.con_trabajo)
            print(f"quitado: {a.id}" + (" (con su trabajo)" if a.con_trabajo else " (su trabajo sigue en uxyngraphar/trabajo/)"))
        elif a.cmd == "indice":
            generar.regenerar(Path(a.repo).resolve())
            print(generar.indice(Path(a.repo).resolve()))
        elif a.cmd == "grupos":
            return cmd_grupos(a)
        elif a.cmd == "completado":
            import completado
            print(completado.script(a.shell), end="")
        elif a.cmd == "diagnostico":
            import diagnostico
            datos = diagnostico.informe(red=not a.sin_red)
            datos = diagnostico.anonimizar(datos) if a.anonimizar else datos
            _json(datos) if a.json else print(diagnostico.texto(datos), end="")
        elif a.cmd == "integracion":
            import integracion
            raiz = Path(a.repo).resolve()
            if a.accion and not a.tipo:
                raise ValueError("indica workflow o precommit")
            if a.accion == "agregar":
                print(f"añadido: {integracion.agregar(raiz, a.tipo)}")
            elif a.accion == "quitar":
                print("quitado" if integracion.quitar(raiz, a.tipo) else "no estaba (o no es de uxyngraphar)")
            else:
                for tipo, puesto in integracion.estado(raiz).items():
                    print(f"{tipo}\t{'puesto' if puesto else '-'}")
        elif a.cmd == "deshacer":
            raiz = Path(a.repo).resolve()
            if a.lista:
                for r in transaccion.listar(raiz):
                    print(f"{r['nombre']}\t{r['fecha']}\tantes de: {r['motivo']}")
                return 0
            r = transaccion.deshacer(raiz, a.respaldo)
            print(f"deshecho: {r['motivo']} ({r['fecha']}); para volver a como estaba: uxyngraphar deshacer --repo {raiz}")
        elif a.cmd == "retirar":
            import desinstalacion
            r = desinstalacion.retirar_de_proyecto(a.repo, a.con_trabajo)
            print("uxyngraphar quitado del proyecto")
            for h in r["hechos"]:
                print(f"  {h}")
            if not a.con_trabajo:
                print("El trabajo propio se conserva (uxyngraphar/trabajo/).")
        else:
            return {"generar": cmd_generar, "estado": cmd_estado, "verificar": cmd_verificar, "flujo": cmd_flujo, "andamiar": cmd_andamiar,
                    "panel": cmd_panel, "proyectos": cmd_proyectos,
                    "flujos-guardados": cmd_flujos_guardados, "accesos": cmd_accesos}[a.cmd](a)
    except (ValueError, FileNotFoundError, FileExistsError, transaccion.ProyectoOcupado,
            remoto.SinServidor, remoto.NoEncontrado) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except OSError as e:   # permisos, disco lleno…: un mensaje, no un traceback
        print(f"error: {e.strerror or e}" + (f": {e.filename}" if getattr(e, "filename", None) else ""), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
