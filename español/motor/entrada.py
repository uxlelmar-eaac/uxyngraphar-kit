"""Bloque de entrada del README.md de cada paquete, generado a partir de su manifiesto (sobre todo de «piezas»).

El bloque va entre marcas; el resto del README es del autor. Así el README no se desfasa al agregar o quitar piezas.
"""

from __future__ import annotations

from pathlib import Path

import especificacion as esp

base = esp.base
INICIO = "<!-- uxyngraphar:entrada:inicio -->"
FIN = "<!-- uxyngraphar:entrada:fin -->"


def bloque(m: dict) -> str:
    pid = m["id"]
    piezas = set(m.get("piezas") or [])
    frases = m.get("activacion") or [pid]
    protocolo = next((f for f in frases if f != pid), pid)
    pasos = ["Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.",
             "Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí."]
    if "limites" in piezas:
        pasos.append("Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.")
    if "proceso" in piezas:
        fases = " → ".join(f"`$P/proceso/{f}.md`" for f in m.get("proceso") or [])
        pasos.append(f"Proceso, en orden: {fases}. Cada fase dice qué skills usar y cuándo está terminada.")
    if "skills" in piezas:
        pasos.append("Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.")
    consulta = [texto for pieza, texto in (("componentes", "`$P/COMPONENTES.md` (piezas que define)"),
                                           ("herramientas", "`$P/HERRAMIENTAS.md` (scripts)"),
                                           ("referencia", "`$P/referencia/` (guías)"),
                                           ("ejemplos", "`$P/ejemplos/` (casos resueltos)")) if pieza in piezas]
    if consulta:
        pasos.append("Consulta cuando haga falta: " + ", ".join(consulta) + ".")
    if "andamiaje" in piezas:
        variantes = ", ".join(f"`{v}`" for v in m.get("andamiaje") or {})
        pasos.append("Andamiaje: `python3 $P/scripts/comun/andamiar.py <variante> --nombre <nombre>` muestra lo que crearía; "
                     f"con `--aplicar` lo crea sin sobrescribir. Variantes: {variantes}.")
    trabajo = f"Trabajo: escribe solo en `uxyngraphar/trabajo/{pid}/`"
    if m.get("fichas"):
        trabajo += " (fichas con `python3 $P/scripts/comun/fichas.py …`)"
    pasos.append(trabajo + " y, en el código del proyecto, solo lo que el pedido pida.")
    verificaciones = ", ".join(f"`python3 $P/{v}`" for v in m.get("verificaciones") or [])
    pasos.append(f"Antes de terminar: {verificaciones or 'sin verificaciones propias'}.")
    lineas = [INICIO,
              f"Activado con «usa el paquete {pid}» / «sigue el protocolo {protocolo}» o por `uxyngraphar/FLUJO.json`. "
              f"Rutas relativas a la raíz de la app. `P={base.CARPETA_PAQUETES}/{pid}`.",
              "",
              *(f"{i}. {p}" for i, p in enumerate(pasos, 1)),
              "",
              "Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.",
              FIN]
    return "\n".join(lineas)


def con_bloque(texto: str, m: dict) -> str:
    """README con el bloque actualizado: reemplaza el que hay entre marcas o lo coloca tras el título."""
    nuevo = bloque(m)
    if INICIO in texto and FIN in texto:
        antes, _, resto = texto.partition(INICIO)
        _, _, despues = resto.partition(FIN)
        return antes + nuevo + despues
    titulo, _, resto = texto.partition("\n")
    return f"{titulo}\n\n{nuevo}\n" + (f"\n{resto.lstrip(chr(10))}" if resto.strip() else "")


def actualizar(carpeta: Path) -> bool:
    """Regenera el bloque del README del paquete; devuelve True si cambió."""
    ruta = Path(carpeta) / base.ENTRADA
    actual = ruta.read_text(encoding="utf-8")
    nuevo = con_bloque(actual, base.leer_manifiesto(carpeta))
    if nuevo != actual:
        ruta.write_text(nuevo, encoding="utf-8")
    return nuevo != actual


def al_dia(carpeta: Path) -> bool:
    ruta = Path(carpeta) / base.ENTRADA
    texto = ruta.read_text(encoding="utf-8")
    return INICIO in texto and con_bloque(texto, base.leer_manifiesto(carpeta)) == texto
