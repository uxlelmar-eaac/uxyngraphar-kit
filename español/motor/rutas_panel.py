"""API del panel: una función por ruta, agrupadas por área (catálogo, proyecto, proyectos, flujos guardados,
herramienta). Cada función recibe los datos del pedido (query o JSON) y devuelve lo que va en «ok»."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import casa
import catalogo
import flujos_guardados as guardados
import generador
import generar
import herramienta
import proyectos
import remoto
import repo

import transaccion

ERRORES_USUARIO = (ValueError, FileNotFoundError, FileExistsError, PermissionError,
                   remoto.SinServidor, remoto.NoEncontrado)   # remoto.SesionRechazada es un PermissionError
ERRORES_CONFLICTO = (transaccion.ProyectoOcupado,)
# Rutas POST que cambian algo y van al registro de auditoría (M-11): ruta → nombre de la acción.
AUDITADAS = {"/api/repo/instalar": "instalar", "/api/sistemas/traer": "traer del servidor", "/api/repo/actualizar": "actualizar", "/api/repo/quitar": "quitar",
             "/api/repo/desinstalar": "retirar", "/api/repo/flujo": "flujo",
             "/api/repo/deshacer": "deshacer", "/api/repo/nomenclatura": "nomenclatura migrar",
             "/api/repo/integracion": "integración de verificar", "/api/grupos/actualizar": "actualizar grupo",
             "/api/repo/memorias/nueva": "nueva memoria", "/api/repo/memorias/aprobar": "aprobar memoria",
             "/api/repo/memorias/archivar": "archivar memoria",
             "/api/grupos/aplicar-flujo": "aplicar flujo al grupo",
             "/api/catalogo/instalar-en": "instalar", "/api/flujos/aplicar": "aplicar flujo",
             "/api/herramienta/proyectos": "actualizar proyectos", "/api/herramienta/desinstalar": "desinstalar",
             "/api/herramienta/actualizar": "actualizar herramienta", "/api/herramienta/usar": "usar versión",
             "/api/herramienta/anterior": "volver a la versión anterior", "/api/herramienta/reparar": "reparar",
             "/api/cuenta/cerrar": "cerrar sesión", "/api/biblioteca/sincronizar": "sincronizar biblioteca",
             "/api/creador/bajar": "bajar borrador del Creador", "/api/creador/subir": "subir borrador al Creador",
             "/api/reportes/enviar": "reportar al autor"}


class FaltaCampo(ValueError):
    pass


class ProyectoNoRegistrado(ValueError):
    pass


class FaltaConfirmacion(ValueError):
    pass


# Códigos de error de la API (M-25): (código, acción que la web puede ofrecer). Documentados en README del motor.
CODIGOS = [
    (FaltaCampo, "campo_obligatorio", ""),
    (ProyectoNoRegistrado, "proyecto_no_registrado", "registrar"),
    (FaltaConfirmacion, "falta_confirmacion", "confirmar"),
    (transaccion.ProyectoOcupado, "proyecto_ocupado", "reintentar"),
    (remoto.DePago, "de_pago", "comprar"),
    (PermissionError, "sin_permiso", ""),
    (FileNotFoundError, "no_encontrado", ""),
    (FileExistsError, "ya_existe", ""),
    (ValueError, "pedido_invalido", ""),
]


def codigo_error(e: BaseException) -> tuple[str, str]:
    """(código, acción) de un error de usuario o de conflicto."""
    import protecciones
    if isinstance(e, protecciones.AjustesClaudeInvalidos):
        return "ajustes_claude_invalidos", "corregir_ajustes"
    return next(((c, a) for tipo, c, a in CODIGOS if isinstance(e, tipo)), ("pedido_invalido", ""))


def _campo(datos: dict, nombre: str, tipo: type | tuple[type, ...] | None = None):
    """Valor obligatorio del pedido; si falta o no es del tipo esperado, un error que la persona entiende."""
    if not isinstance(datos, dict) or datos.get(nombre) is None:
        raise FaltaCampo(f"falta el campo «{nombre}»")
    valor = datos[nombre]
    if tipo is not None and not isinstance(valor, tipo):
        nombres = {list: "una lista", str: "un texto", dict: "un objeto", bool: "verdadero o falso"}
        esperado = nombres.get(tipo, getattr(tipo, "__name__", str(tipo))) if isinstance(tipo, type) else "otro tipo"
        raise ValueError(f"el campo «{nombre}» debe ser {esperado}")
    return valor


def _retirar(raiz: Path, con_trabajo: bool) -> dict:
    import desinstalacion
    return desinstalacion.retirar_de_proyecto(str(raiz), con_trabajo)


def _prohibida(ruta: Path) -> str:
    """Motivo por el que una carpeta nunca es un proyecto (vacío si puede serlo)."""
    ruta = ruta.resolve()
    if ruta.parent == ruta:
        return "es la raíz del sistema"
    if proyectos.misma_carpeta(str(ruta), str(Path.home())):
        return "es tu carpeta personal"
    datos = casa.carpeta().resolve()
    if ruta == datos or datos in ruta.parents or ruta in datos.parents:
        return "es (o contiene) la carpeta de datos de uxyngraphar"
    return ""


def _parece_proyecto(ruta: Path) -> bool:
    return (ruta / ".git").exists() or (ruta / repo.base.CARPETA_RAIZ).is_dir()


def comprobar_carpeta(ruta: Path, datos: dict | None = None) -> None:
    """Lo que hace falta para registrar una carpeta como proyecto: no es /, ni la carpeta personal, ni la de datos, y
    parece un proyecto (repo git o con uxyngraphar) o la persona lo confirma con su nombre en «confirmar»."""
    motivo = _prohibida(ruta)
    if motivo:
        raise ValueError(f"{ruta} {motivo}: elige la carpeta de un proyecto")
    if not _parece_proyecto(ruta) and str((datos or {}).get("confirmar") or "") != ruta.name:
        raise ValueError(f"{ruta} no es un repositorio git ni tiene uxyngraphar: si de verdad es un proyecto, "
                         f"confírmalo enviando «confirmar»: «{ruta.name}»")


def _raiz(datos: dict, escribir: bool = False) -> Path:
    """Carpeta del proyecto del pedido. Para consultar basta con que exista; para cambiar algo tiene que estar
    registrado en «Mis proyectos» (registrar es una acción aparte)."""
    texto = str((datos or {}).get("repo") or "").strip()
    if not texto:
        raise FaltaCampo("falta el campo «repo»")
    ruta = Path(texto).expanduser()
    if not ruta.is_dir():
        raise ValueError("indica la carpeta de un proyecto que exista")
    ruta = ruta.resolve()
    if escribir:
        motivo = _prohibida(ruta)
        if motivo:
            raise ValueError(f"{ruta} {motivo}: no se puede cambiar")
        if not proyectos.registrado(str(ruta)):
            raise ProyectoNoRegistrado(f"{ruta} no está en «Mis proyectos»: añádelo primero (botón «Añadirlo a mis proyectos» o "
                             f"«uxyngraphar proyectos agregar {ruta}»)")
    return ruta


def _confirmado(raiz: Path, datos: dict, accion: str) -> None:
    """Las acciones que borran trabajo o lo mueven exigen «confirmar» con el nombre de la carpeta del proyecto."""
    if str(datos.get("confirmar") or "") != raiz.name:
        raise FaltaConfirmacion(f"{accion}: confirma enviando «confirmar»: «{raiz.name}» (el nombre de la carpeta del proyecto)")


def _escribible(d: dict, accion: str = "", destructiva: bool = False) -> Path:
    raiz = _raiz(d, escribir=True)
    if destructiva:
        _confirmado(raiz, d, accion)
    return raiz


def _flujo_sin_escribir(raiz: Path) -> dict:
    """FLUJO.json del proyecto o, si aún no existe, el inicial en memoria: consultar nunca escribe en el proyecto."""
    return generar.leer_flujo(raiz) if generar.ruta_flujo(raiz).is_file() else dict(generar.esp.FLUJO_INICIAL)


def _estado_repo(d: dict) -> dict:
    raiz = _raiz(d)
    datos: dict = {"ruta": str(raiz), "nombre": raiz.name, "sistemas": repo.estado(raiz), "flujo": None,
                   "registrado": proyectos.registrado(str(raiz))}
    import vocabulario
    datos["vocabulario_pendiente"] = vocabulario.pendientes(raiz)
    datos["memorias_propuestas"] = __import__("memorias_repo").propuestas(raiz)
    if datos["sistemas"] or generar.ruta_flujo(raiz).is_file():
        datos["flujo"] = _flujo_sin_escribir(raiz)
    return datos


def _guardar_flujo(d: dict) -> dict:
    errores = generar.guardar_flujo(_escribible(d), _campo(d, "flujo", dict))
    if errores:
        raise ValueError("; ".join(errores))
    return {"errores": []}


def _bienvenida(_d: dict) -> dict:
    datos = casa.leer_json("ultima-instalacion.json", {})
    home = str(casa.carpeta())
    return {**datos, "en_path": herramienta.ar.en_path(herramienta.ar.carpeta_bin(home)), "accesos": herramienta.accesos()}


def version() -> dict:
    return {"version": herramienta.version(), "instalada": herramienta.instalada()}


def _servidor(d: dict) -> dict:
    """Búsqueda en el servidor de sistemas de gobernanza. Sin red responde con «error» (el panel lo muestra) y lo guardado."""
    import fuentes
    salida: dict[str, Any] = {"servidor": None, "error": "", "sistemas": [], "locales": fuentes.locales()}
    try:
        salida["servidor"] = remoto.servidor()
        salida["sistemas"] = remoto.buscar(str(d.get("q") or ""), str(d.get("familia") or ""))
    except (remoto.SinServidor, ValueError) as e:
        salida["error"] = str(e)
    traidos = {(m.parent.parent.parent.name, m.parent.parent.name, m.parent.name)
               for m in remoto.cache().glob(f"*/*/*/{remoto.MARCA_COMPLETO}")} if remoto.cache().is_dir() else set()
    for s in salida["sistemas"]:
        s["traido"] = sorted(v for e, i, v in traidos if e == s.get("editor") and i == s.get("id"))
    return salida


def _cuenta(d: dict) -> dict:
    """Tarjeta «Cuenta» (K01): con qué cuenta está conectado este equipo. «comprobar» pregunta al servidor."""
    datos = remoto.sesion()
    salida: dict[str, Any] = {"servidor": None, "tipo": datos.get("tipo") or "ninguna", "usuario": datos.get("usuario"),
                              "equipo": datos.get("equipo"), "valida": None, "error": ""}
    try:
        salida["servidor"] = remoto.servidor()
    except remoto.SinServidor as e:
        salida["error"] = str(e)
    if datos.get("tipo") == "sesion" and d.get("comprobar"):
        try:
            yo = remoto.quien_soy()
            salida.update(usuario=yo.get("usuario"), equipo=yo.get("equipo"), valida=True)
        except PermissionError:
            salida["valida"] = False
        except remoto.SinServidor as e:
            salida["error"] = str(e)
    return salida


def _cuenta_consultar(d: dict) -> dict:
    r = remoto.consultar_codigo(_campo(d, "codigo_dispositivo", str))
    if r["estado"] == "aprobado":
        sincronizar_en_fondo()
    return r


# ── biblioteca sincronizada (ADR 0012): al abrir el panel, al iniciar sesión y a petición ─────────────────────

_SINCRONIA: dict[str, Any] = {"en_curso": False, "cuando": None, "resultado": None, "error": ""}
_CANDADO_SINCRONIA = threading.Lock()


def _sincronizar() -> None:
    import fuentes
    try:
        r = fuentes.sincronizar_biblioteca()
        _SINCRONIA.update(resultado=r, error="")
    except (remoto.SinServidor, PermissionError, OSError, ValueError) as e:
        _SINCRONIA["error"] = str(e)
    finally:
        _SINCRONIA.update(en_curso=False, cuando=time.time())


def sincronizar_en_fondo(esperar: bool = False) -> bool:
    """Arranca la sincronización si hay sesión del kit y no hay otra en curso. Nunca toca los repos."""
    if remoto.sesion().get("tipo") != "sesion":
        return False
    with _CANDADO_SINCRONIA:
        if _SINCRONIA["en_curso"]:
            return False
        _SINCRONIA["en_curso"] = True
    hilo = threading.Thread(target=_sincronizar, daemon=True, name="uxy-sincronizar")
    hilo.start()
    if esperar:
        hilo.join()
    return True


def _biblioteca(_d: dict) -> dict:
    """Lo que el panel muestra de la biblioteca: lo guardado (sirve sin red) y la última sincronización."""
    datos = remoto.sesion()
    sistemas = []
    for s in remoto._sistemas_biblioteca():  # noqa: SLF001 - lectura de la caché propia
        version = (s["versiones"] or [{}])[0].get("version")
        sistemas.append({"editor": s["editor"], "id": s["id"], "titulo": s["titulo"], "version": version,
                         "origen": s.get("origen"), "de_pago": s.get("de_pago"), "privado": s.get("privado"),
                         "traido": bool(version and remoto.en_cache(s["editor"], s["id"], version))})
    return {"sesion": datos.get("tipo") == "sesion", "usuario": datos.get("usuario"), "sistemas": sistemas,
            **{k: _SINCRONIA[k] for k in ("en_curso", "cuando", "resultado", "error")}}


def _biblioteca_sincronizar(d: dict) -> dict:
    if remoto.sesion().get("tipo") != "sesion":
        raise PermissionError("sin sesión: inicia sesión en la tarjeta «Cuenta» para sincronizar tu biblioteca")
    sincronizar_en_fondo(esperar=bool(d.get("esperar")))
    return _biblioteca(d)


# ── Creador local (ADR 0013): borradores de la web e IA (modelos de este equipo o la clave de tu cuenta) ────────

def _creador_sincronizar(accion: str, d: dict) -> dict:
    import creador
    conservar = d.get("conservar") or None
    if conservar not in (None, "web", "local"):
        raise ValueError("conservar: web o local")
    try:
        return (creador.bajar if accion == "bajar" else creador.subir)(_campo(d, "slug", str), conservar)
    except creador.Conflicto as e:
        return {"conflicto": True, "slug": e.slug, "revision_web": e.revision_web, "diferencias": e.diferencias}


def _ia(d: dict) -> tuple[str, str]:
    return _campo(d, "proveedor", str), str(d.get("modelo") or "")


def _creador_mejorar(d: dict) -> dict:
    import ia_local
    pid, rel = _campo(d, "id", str), _campo(d, "rel", str)
    original = d["contenido"] if isinstance(d.get("contenido"), str) else catalogo.leer_archivo(pid, rel)
    r = ia_local.mejorar(*_ia(d), rel, original, str(d.get("instruccion") or ""))
    return {"id": pid, "rel": rel, "original": original, "propuesta": r["propuesta"], "modelo": r["modelo"]}


def _creador_revisar(d: dict) -> dict:
    import creador
    import ia_local
    pid = _campo(d, "id", str)
    return ia_local.revisar(*_ia(d), creador.leer(catalogo.catalogo(), pid))


def _creador_chat(d: dict) -> dict:
    import creador
    import ia_local
    pid = _campo(d, "id", str)
    archivos = creador.leer(catalogo.catalogo(), pid)
    contexto = "\n\n".join(f"=== {r} ===\n{t}" for r, t in sorted(archivos.items()))[:60_000]
    simulador = bool(d.get("simulador"))
    sistema = (("Actúa como el agente que trabaja con este sistema de gobernanza: sigue sus reglas, límites y "
                "permisos al pie de la letra y dilo cuando algo no te lo permite.") if simulador else
               "Ayudas a escribir este sistema de gobernanza de uxyngraphar. Responde en español, breve y concreto.")
    proveedor, modelo = _ia(d)
    return ia_local.completar(proveedor, list(_campo(d, "mensajes", list)),
                              f"{sistema}\n\nArchivos del sistema:\n{contexto}", modelo)


GET = {
    # cuenta (sesión del kit en este equipo)
    "/api/cuenta": _cuenta,
    "/api/biblioteca": _biblioteca,
    # servidor de sistemas de gobernanza
    "/api/sistemas/buscar": _servidor,
    # catálogo
    "/api/catalogo": lambda d: catalogo.listar(),
    "/api/catalogo/archivos": lambda d: catalogo.archivos(_campo(d, "id")),
    "/api/catalogo/archivo": lambda d: {"contenido": catalogo.leer_archivo(_campo(d, "id"), _campo(d, "rel"))},
    "/api/catalogo/completitud": lambda d: catalogo.completitud(_campo(d, "id")),
    "/api/catalogo/pendientes": lambda d: generador.pendientes(_campo(d, "id")),
    "/api/catalogo/plantilla-spec": lambda d: generador.plantilla_spec(d.get("id") or "contratos-de-pago", d.get("familia") or "proceso"),
    # Creador local
    "/api/creador/modelos": lambda d: __import__("ia_local").modelos(),
    "/api/creador/borradores": lambda d: __import__("creador").borradores(),
    # un proyecto
    "/api/repo/estado": _estado_repo,
    "/api/repo/flujo": lambda d: _flujo_sin_escribir(_raiz(d)),
    "/api/repo/respaldos": lambda d: transaccion.listar(_raiz(d)),
    "/api/repo/integracion": lambda d: __import__("integracion").estado(_raiz(d)),
    "/api/repo/memorias": lambda d: __import__("memorias_repo").listar(_raiz(d)),
    # proyectos registrados
    "/api/proyectos": lambda d: proyectos.resumenes(),
    "/api/proyectos/carpetas": lambda d: proyectos.carpetas(d.get("ruta") or None),
    "/api/proyectos/buscar": lambda d: proyectos.buscar(_campo(d, "ruta")),
    # flujos guardados
    "/api/flujos": lambda d: guardados.listar(),
    "/api/flujos/exportar": lambda d: guardados.exportar(_campo(d, "id")),
    # herramienta
    "/api/herramienta": lambda d: herramienta.info(),
    "/api/herramienta/ultima": lambda d: herramienta.ultima(bool(d.get("forzar"))),
    "/api/herramienta/progreso": lambda d: herramienta.progreso(),
    "/api/accesos": lambda d: herramienta.accesos(),
    "/api/bienvenida": _bienvenida,
    "/api/avisos": lambda d: __import__("diagnostico").avisos(),
    "/api/diagnostico": lambda d: _diagnostico(d),  # noqa: PLW0108 - _diagnostico se define más abajo
    "/api/grupos": lambda d: __import__("grupos").listar(),
    "/api/grupos/matriz": lambda d: __import__("grupos").matriz(_campo(d, "nombre", str)),
    "/api/historial": lambda d: __import__("auditoria").leer(int(d.get("limite") or 100)),
}

POST = {
    "/api/cuenta/iniciar": lambda d: remoto.pedir_codigo(str(d.get("equipo") or "") or None),
    "/api/cuenta/consultar": _cuenta_consultar,
    "/api/cuenta/cerrar": lambda d: remoto.cerrar_sesion(),
    "/api/biblioteca/sincronizar": _biblioteca_sincronizar,
    "/api/creador/bajar": lambda d: _creador_sincronizar("bajar", d),
    "/api/creador/subir": lambda d: _creador_sincronizar("subir", d),
    "/api/creador/mejorar": _creador_mejorar,
    "/api/creador/revisar": _creador_revisar,
    "/api/creador/chat": _creador_chat,
    "/api/reportes/vista-previa": lambda d: _reporte(d, enviar=False),
    "/api/reportes/enviar": lambda d: _reporte(d, enviar=True),
    "/api/sistemas/traer": lambda d: {"ruta": str(remoto.traer(_campo(d, "ref", str)))},
    # catálogo (modo avanzado)
    "/api/catalogo/crear": lambda d: str(catalogo.crear(_campo(d, "id"), _campo(d, "titulo"), d.get("descripcion", ""), familia=d.get("familia", "proceso"),
                                                        piezas=d.get("piezas"))),
    "/api/catalogo/generar": lambda d: generador.desde_spec(_campo(d, "spec"), aplicar=bool(d.get("aplicar"))),
    "/api/catalogo/pieza": lambda d: (catalogo.agregar_pieza if _campo(d, "accion") == "agregar" else catalogo.quitar_pieza)(_campo(d, "id"), _campo(d, "pieza")),
    "/api/catalogo/archivo": lambda d: {"errores": catalogo.guardar_archivo(_campo(d, "id"), _campo(d, "rel"), _campo(d, "contenido"))},
    "/api/catalogo/version": lambda d: catalogo.versionar(_campo(d, "id"), _campo(d, "nivel")),
    "/api/catalogo/instalar-en": lambda d: [_instalar_en(r, list(_campo(d, "ids", list))) for r in _campo(d, "repos", list)],
    # un proyecto
    "/api/repo/instalar": lambda d: repo.instalar(_escribible(d), list(_campo(d, "ids", list)), sistema_base=d.get("base") or None),
    "/api/repo/actualizar": lambda d: repo.actualizar(_escribible(d), list(d.get("ids") or []) or None, forzar=bool(d.get("forzar"))),
    "/api/repo/quitar": lambda d: repo.quitar(_escribible(d, "quitar con su trabajo", bool(d.get("con_trabajo"))), _campo(d, "id", str),
                                              bool(d.get("con_trabajo"))),
    "/api/repo/desinstalar": lambda d: _retirar(_escribible(d, "retirar con el trabajo", bool(d.get("con_trabajo"))),
                                                bool(d.get("con_trabajo"))),
    "/api/repo/verificar": lambda d: repo.verificar(_escribible(d)),
    "/api/repo/flujo": _guardar_flujo,
    "/api/repo/nomenclatura": lambda d: __import__("vocabulario").aplicar(_escribible(d, "migrar el vocabulario", destructiva=True)),
    "/api/repo/integracion": lambda d: _integracion(d),  # noqa: PLW0108 - _integracion se define más abajo
    "/api/repo/memorias/nueva": lambda d: {"id": __import__("memorias_repo").crear(
        _escribible(d), _campo(d, "sistema", str), _campo(d, "slug", str), _campo(d, "titulo", str), str(d.get("texto") or ""),
        str(d.get("motivo") or ""), str(d.get("fuente") or ""), d.get("valida_hasta") or None)},
    "/api/repo/memorias/aprobar": lambda d: {"id": __import__("memorias_repo").aprobar(_escribible(d), _campo(d, "sistema", str), _campo(d, "id", str))},
    "/api/repo/memorias/archivar": lambda d: {"id": __import__("memorias_repo").archivar(_escribible(d), _campo(d, "sistema", str), _campo(d, "id", str))},
    "/api/grupos/guardar": lambda d: __import__("grupos").guardar(_campo(d, "nombre", str), _campo(d, "rutas", list)),
    "/api/grupos/borrar": lambda d: __import__("grupos").borrar(_campo(d, "nombre", str)),
    "/api/grupos/actualizar": lambda d: __import__("grupos").actualizar(_campo(d, "nombre", str)),
    "/api/grupos/verificar": lambda d: __import__("grupos").verificar(_campo(d, "nombre", str)),
    "/api/grupos/aplicar-flujo": lambda d: __import__("grupos").aplicar_flujo(_campo(d, "nombre", str), _campo(d, "id", str)),
    "/api/repo/deshacer": lambda d: transaccion.deshacer(_escribible(d, "deshacer", destructiva=True), d.get("respaldo") or None),
    # proyectos registrados
    "/api/proyectos/agregar": lambda d: _agregar(d),  # noqa: PLW0108 - _agregar se define más abajo
    "/api/proyectos/quitar": lambda d: proyectos.quitar(_campo(d, "ruta")),
    # flujos guardados
    "/api/flujos/guardar": lambda d: guardados.guardar(_campo(d, "flujo")),
    "/api/flujos/desde-proyecto": lambda d: guardados.desde_proyecto(_raiz(d), _campo(d, "nombre", str), d.get("descripcion", "")),
    "/api/flujos/aplicar": lambda d: guardados.aplicar(_campo(d, "id", str), _registrados(_campo(d, "repos", list))),
    "/api/flujos/duplicar": lambda d: guardados.duplicar(_campo(d, "id")),
    "/api/flujos/borrar": lambda d: guardados.borrar(_campo(d, "id")),
    "/api/flujos/importar": lambda d: guardados.importar(_campo(d, "datos")),
    # herramienta
    "/api/herramienta/actualizar": lambda d: herramienta.actualizar(str(d.get("version") or "")),
    "/api/herramienta/usar": lambda d: herramienta.usar(_campo(d, "version")),
    "/api/herramienta/proyectos": lambda d: herramienta.actualizar_proyectos(),
    "/api/herramienta/anterior": lambda d: herramienta.volver_anterior(),
    "/api/herramienta/reparar": lambda d: herramienta.reparar(bool(d.get("proyectos"))),
    "/api/herramienta/desinstalar": lambda d: herramienta.desinstalar(str(d.get("alcance") or "herramienta"),
                                                                      list(d.get("rutas") or []), bool(d.get("con_trabajo")),
                                                                      bool(d.get("simular"))),
    "/api/herramienta/path": lambda d: herramienta.agregar_path(),
    "/api/accesos": lambda d: herramienta.cambiar_accesos(list(d.get("tipos") or [])),
}


def _reporte(d: dict, enviar: bool) -> dict:
    """Vista previa (lo que saldría del equipo) o envío de exactamente eso; ver `reportes`."""
    import reportes
    datos = reportes.armar(_campo(d, "ref", str), _campo(d, "tipo", str), _campo(d, "texto", str),
                           _raiz(d) if d.get("repo") else None)
    salida = {"datos": datos, "vista_previa": reportes.vista_previa(datos)}
    return {**salida, **reportes.enviar(datos)} if enviar else salida


def _instalar_en(ruta: str, ids: list[str]) -> dict:
    """Instala en un proyecto los sistemas que aún no tenga (para instalar desde el catálogo en varios a la vez)."""
    fila = {"ruta": ruta, "instalados": [], "error": ""}
    try:
        raiz = _raiz({"repo": ruta}, escribir=True)
        faltan = [p for p in ids if not repo.carpeta_instalada(raiz, p).exists()]
        fila["instalados"] = repo.instalar(raiz, faltan) if faltan else []
    except ERRORES_USUARIO + ERRORES_CONFLICTO as e:
        fila["error"] = str(e)
    return fila


def _diagnostico(d: dict) -> dict:
    import diagnostico
    datos = diagnostico.informe()
    return diagnostico.anonimizar(datos) if d.get("anonimizar") else datos


def _integracion(d: dict) -> dict:
    import integracion
    raiz = _escribible(d)
    tipo, accion = _campo(d, "tipo", str), _campo(d, "accion", str)
    if accion not in ("agregar", "quitar"):
        raise ValueError("accion: agregar o quitar")
    integracion.agregar(raiz, tipo) if accion == "agregar" else integracion.quitar(raiz, tipo)
    return integracion.estado(raiz)


def _registrados(rutas: list) -> list[str]:
    """Solo proyectos registrados: aplicar un flujo instala sistemas y escribe FLUJO.json."""
    return [str(_raiz({"repo": r}, escribir=True)) for r in rutas]


def _agregar(d: dict) -> list[str]:
    rutas = list(d.get("rutas") or ([d["ruta"]] if d.get("ruta") else []))
    if not rutas:
        raise FaltaCampo("falta el campo «rutas»")
    for r in rutas:
        ruta = Path(str(r or "")).expanduser()
        if ruta.is_dir():
            comprobar_carpeta(ruta.resolve(), d if len(rutas) == 1 else None)
    return proyectos.agregar(rutas)
