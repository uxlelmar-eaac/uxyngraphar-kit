"""Archivos generados por el motor en un repo: uxyngraphar/INDICE.md, bloque de AGENTES.md/AGENTS.md/CLAUDE.md y FLUJO.json
inicial. El bloque es el mismo y completo en los tres archivos: cada agente lee solo el suyo (Claude Code, CLAUDE.md;
Codex y otros, AGENTS.md) y no se puede confiar en que siga un puntero a otro archivo."""

from __future__ import annotations

import json
from pathlib import Path

import especificacion as esp
import protecciones

base = esp.base
INICIO = "<!-- uxyngraphar:inicio -->"
FIN = "<!-- uxyngraphar:fin -->"
ARCHIVOS_AGENTE = ("AGENTES.md", "AGENTS.md", "CLAUDE.md")
# Archivos de otros agentes que se mantienen con el bloque solo si el proyecto ya los tiene (M-15).
OPCIONALES = (".github/copilot-instructions.md",)

BLOQUE = f"""{INICIO}
## uxyngraphar — sistemas de gobernanza

Este proyecto tiene sistemas de gobernanza en `uxyngraphar/` (índice: `uxyngraphar/INDICE.md`). La persona decide cómo trabajas en `uxyngraphar/FLUJO.json`. Rutas relativas a la carpeta de este archivo.

1. **No leas ni apliques ningún sistema** salvo que el pedido diga «usa el sistema de gobernanza <frase>», «usa el sistema <frase>» o «sigue el protocolo <frase>» (frases en `INDICE.md`) o que `FLUJO.json` lo indique. Lee `FLUJO.json` al empezar cada pedido:
   - `manual`: solo sistemas nombrados en el pedido.
   - `leer_por_defecto`: lee el `README.md` de esos sistemas en cada pedido; aplica solo los nombrados.
   - `trabajar_con`: ese es el sistema base: aplícalo en **cada** pedido aunque no lo nombre; si el pedido nombra otros, aplícalos también.
   - `secuencia`: recorre esos sistemas en orden.
2. **Al activar un sistema `<id>`:** ejecuta `python3 uxyngraphar/sistemas-de-gobernanza/<id>/scripts/comun/verificar-integridad.py`; si falla, detente y avisa. Luego lee `uxyngraphar/sistemas-de-gobernanza/<id>/README.md`: dice en qué orden leer su alcance (`SISTEMA.md`), sus memorias (`MEMORIAS.md` y `scripts/comun/memorias.py listar`), sus límites y permisos (`LIMITES.md` y `PERMISOS.md`), su proceso por fases y sus skills. Si el pedido cae fuera de su alcance, dilo y no lo resuelvas con ese sistema. Ejecuta sus `verificaciones` antes de terminar.
   - **Memorias del proyecto** (`uxyngraphar/trabajo/<id>/memorias/`): aplica las vigentes; lo que valga la pena recordar, propónlo con `memorias.py nueva` (queda «propuesta»). Nunca las apruebes ni las archives: eso lo hace la persona.
3. **Escribe solo en `uxyngraphar/trabajo/<id>/`** de los sistemas activos. Nunca crees, edites ni borres nada en `uxyngraphar/sistemas-de-gobernanza/`, `uxyngraphar/FLUJO.json`, `uxyngraphar/INDICE.md` ni los `ajustes.json` de `uxyngraphar/trabajo/`: son de la persona y del panel.
4. **Lo que decide una persona lo ejecuta una persona.** Nunca ejecutes las acciones de «Solo una persona» del `PERMISOS.md` de cada sistema ni uses `--humano` ni `UXYNGRAPHAR_HUMANO`: deja la ficha lista y di qué comando debe ejecutar la persona.
5. **Si dos sistemas activos se contradicen, detente y pregunta.**
{{extra}}{FIN}
"""


def bloque(manifiestos: list[dict] | None = None) -> str:
    """Bloque de AGENTES.md; los sistemas con «al_activar_sistema» añaden un paso a cada activación."""
    pasos = [f"   - `python3 {base.CARPETA_SISTEMAS_DE_GOBERNANZA}/{m['id']}/{m['al_activar_sistema']}` ({m['id']})"
             for m in manifiestos or [] if m.get("al_activar_sistema")]
    extra = ("6. **Con cada sistema `<id>` que actives**, ejecuta también (sustituye `{id}`) y sigue lo que indique:\n"
             + "\n".join(pasos) + "\n") if pasos else ""
    return BLOQUE.replace("{extra}", extra)


def instalados(raiz_app: Path) -> list[dict]:
    """Manifiestos de los sistemas presentes en `<raiz>/uxyngraphar/sistemas-de-gobernanza/` (ignora carpetas temporales y no-sistemas)."""
    carpeta = Path(raiz_app) / base.CARPETA_SISTEMAS_DE_GOBERNANZA
    if not carpeta.is_dir():
        return []
    salida = []
    for c in sorted(carpeta.iterdir()):
        if c.is_dir() and not c.name.startswith(".") and (c / base.MANIFIESTO).is_file():
            try:
                salida.append(base.leer_manifiesto(c))
            except ValueError:
                salida.append({"id": c.name, "version": "?", "titulo": "(manifiesto ilegible)", "activacion": [], "descripcion": ""})
    return salida


def indice(raiz_app: Path) -> Path:
    sistemas = instalados(raiz_app)
    lineas = ["# uxyngraphar — sistemas instalados", "",
              "Generado por el motor; no editar. Cada sistema de gobernanza se activa con «usa el sistema <frase>» (o «usa el sistema de gobernanza <frase>») o «sigue el protocolo <frase>».",
              "Sistemas: `sistemas-de-gobernanza/<id>/`. Trabajo de cada sistema: `trabajo/<id>/` (memorias del proyecto en `trabajo/<id>/memorias/`). Flujo del agente: `FLUJO.json`.", ""]
    if not sistemas:
        lineas.append("(sin sistemas instalados)")
    else:
        lineas += ["| Sistema | Versión | Frases de activación | Qué gobierna | Problemas que cubre | Entrada |", "|---|---|---|---|---|---|"]
        for m in sistemas:
            frases = ", ".join(f"«{f}»" for f in m.get("activacion", []))
            problemas = ", ".join(f"`{p}`" for p in sorted(base.ids_problemas(m))) or "—"
            lineas.append(f"| {m.get('titulo', m['id'])} (`{m['id']}`) | {m.get('version', '?')} | {frases} | "
                          f"{m.get('descripcion', '')} | {problemas} | `sistemas-de-gobernanza/{m['id']}/{base.ENTRADA}` |")
    destino = Path(raiz_app) / base.CARPETA_RAIZ / esp.INDICE
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return destino


def insertar_bloque(texto: str, manifiestos: list[dict] | None = None) -> str:
    """Reemplaza el bloque entre marcas o lo añade al final, sin tocar el resto del archivo."""
    nuevo = bloque(manifiestos)
    if INICIO in texto and FIN in texto:
        antes, _, resto = texto.partition(INICIO)
        _, _, despues = resto.partition(FIN)
        return antes + nuevo.rstrip("\n") + despues
    separador = "" if not texto else ("\n" if texto.endswith("\n") else "\n\n")
    return texto + separador + nuevo


def quitar_bloque(texto: str) -> str:
    if INICIO not in texto or FIN not in texto:
        return texto
    antes, _, resto = texto.partition(INICIO)
    _, _, despues = resto.partition(FIN)
    return (antes.rstrip("\n") + "\n" + despues.lstrip("\n")).lstrip("\n")


def agentes(raiz_app: Path) -> list[Path]:
    """Escribe el bloque en AGENTES.md, AGENTS.md y CLAUDE.md de la raíz de la app (los crea si faltan; respeta enlaces y
    el resto del contenido de cada archivo)."""
    escritos = []
    manifiestos = instalados(raiz_app)
    for nombre in (*ARCHIVOS_AGENTE, *OPCIONALES):
        ruta = Path(raiz_app) / nombre
        if ruta.is_symlink() or (nombre in OPCIONALES and not ruta.is_file()):
            continue
        actual = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
        base_texto = actual
        nuevo = insertar_bloque(base_texto, manifiestos)
        if nuevo != actual:
            ruta.write_text(nuevo, encoding="utf-8")
        escritos.append(ruta)
    return escritos


def ruta_flujo(raiz_app: Path) -> Path:
    return Path(raiz_app) / base.CARPETA_RAIZ / esp.FLUJO


def flujo_inicial(raiz_app: Path) -> Path:
    """Crea FLUJO.json en modo manual si no existe; nunca sobrescribe el de la persona."""
    ruta = ruta_flujo(raiz_app)
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(esp.FLUJO_INICIAL, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta


def leer_flujo(raiz_app: Path) -> dict:
    return json.loads(ruta_flujo(raiz_app).read_text(encoding="utf-8"))


def guardar_flujo(raiz_app: Path, flujo: dict) -> list[str]:
    """Guarda FLUJO.json si valida contra los sistemas instalados; devuelve los errores (vacío = guardado)."""
    errores = esp.validar_flujo(flujo, {m["id"] for m in instalados(raiz_app)})
    if not errores:
        ruta = ruta_flujo(raiz_app)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(flujo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        registrar_huella_flujo(raiz_app)
    return errores


def registrar_huella_flujo(raiz_app: Path) -> None:
    """Guarda fuera del repo (carpeta de datos de uxyngraphar) la huella del FLUJO.json que acaba de escribir el motor:
    verificar-integridad.py avisa si después cambia por otra vía (M-15)."""
    ruta = base.ruta_huella_flujo(raiz_app)
    flujo = ruta_flujo(raiz_app)
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps({"FLUJO.json": base.sha256(flujo) if flujo.is_file() else None}) + "\n", encoding="utf-8")
    except OSError:
        pass


def regenerar(raiz_app: Path, anteriores: list[dict] | None = None) -> None:
    indice(raiz_app)
    agentes(raiz_app)
    flujo_inicial(raiz_app)
    protecciones.aplicar(raiz_app, instalados(raiz_app), anteriores)
    registrar_huella_flujo(raiz_app)
