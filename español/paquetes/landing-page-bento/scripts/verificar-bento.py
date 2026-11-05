#!/usr/bin/env python3
"""Verifica el mosaico y la checklist de cada landing. Código 0 = sin errores.

En `borrador` los problemas del mosaico son avisos; desde `en-curso` son errores. En `revision` y `publicada` la checklist
debe estar completa. Límites en los ajustes del paquete (columnas, tamaños, celdas, palabras).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
ESTRICTOS = {"en-curso", "revision", "publicada"}
CHECKLIST_COMPLETA = {"revision", "publicada"}
CTAS = {"primario", "secundario", "-", ""}


def seccion(cuerpo: str, titulo: str) -> list[str]:
    dentro, lineas = False, []
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            dentro = linea[3:].strip().lower() == titulo
            continue
        if dentro:
            lineas.append(linea)
    return lineas


def celdas(cuerpo: str) -> list[list[str]]:
    filas = []
    for linea in seccion(cuerpo, "mosaico"):
        if linea.startswith("|"):
            c = [x.strip() for x in linea.strip().strip("|").split("|")]
            if c and c[0] not in ("#", "") and not set(c[0]) <= set("-: "):
                filas.append((c + [""] * 7)[:7])
    return filas


def problemas_mosaico(filas: list[list[str]], aj: dict) -> list[str]:
    salida = []
    n, columnas = len(filas), int(aj.get("columnas", 4))
    if not filas:
        return ["el mosaico está vacío"]
    if not aj.get("celdas_min", 0) <= n <= aj.get("celdas_max", 99):
        salida.append(f"{n} celdas; deben ser entre {aj.get('celdas_min')} y {aj.get('celdas_max')}")
    areas, prioridades, primarios = {}, [], 0
    for num, tam, prio, titulo, mensaje, cta, medio in filas:
        if tam not in aj.get("tamanos", []):
            salida.append(f"celda {num}: tamaño «{tam}» no permitido ({', '.join(aj.get('tamanos', []))})")
        else:
            ancho, alto = (int(x) for x in tam.split("x"))
            if ancho > columnas:
                salida.append(f"celda {num}: {tam} no cabe en {columnas} columnas")
            areas[num] = ancho * alto
        prioridades.append(prio)
        if len(titulo.split()) > aj.get("palabras_titulo", 99) or not titulo:
            salida.append(f"celda {num}: título vacío o de más de {aj.get('palabras_titulo')} palabras")
        if len(mensaje.split()) > aj.get("palabras_mensaje", 999):
            salida.append(f"celda {num}: mensaje de más de {aj.get('palabras_mensaje')} palabras")
        if cta.lower() not in CTAS:
            salida.append(f"celda {num}: CTA «{cta}» (usa primario, secundario o -)")
        primarios += cta.lower() == "primario"
        m = medio.lower()
        if (m.startswith(("img:", "video:")) and not medio.split(":", 1)[1].strip()) or m in ("img", "video", "imagen"):
            salida.append(f"celda {num}: medio sin texto alternativo (img: <alt>)")
    if sorted(prioridades) != [str(i) for i in range(1, n + 1)]:
        salida.append(f"prioridades deben ser 1..{n} sin repetir")
    if primarios != 1:
        salida.append(f"debe haber exactamente un CTA primario (hay {primarios})")
    if sum(1 for f in filas if f[1] == "2x2") > aj.get("max_2x2", 1):
        salida.append(f"más de {aj.get('max_2x2')} celdas 2x2")
    protagonista = next((f[0] for f in filas if f[2] == "1"), None)
    if protagonista in areas and areas[protagonista] < max(areas.values()):
        salida.append("la celda de prioridad 1 no es la más grande")
    if areas and len(areas) == n and sum(areas.values()) % columnas:
        salida.append(f"la suma de áreas ({sum(areas.values())}) no llena filas de {columnas} columnas: hay huecos")
    return salida


def main() -> int:
    aj = base.leer_ajustes(PAQUETE)
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    errores, avisos = [], []
    for f in fichas.listar(PAQUETE, "landing"):
        _, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(trabajo).as_posix()
        if f.status in ("archivada", "cancelada"):
            continue
        destino = errores if f.status in ESTRICTOS else avisos
        destino += [f"{rel}: {p}" for p in problemas_mosaico(celdas(cuerpo), aj)]
        pendientes = [l.strip()[6:] for l in seccion(cuerpo, "checklist de publicación") if l.strip().startswith("- [ ]")]
        if pendientes and f.status in CHECKLIST_COMPLETA:
            errores.append(f"{rel}: checklist incompleta en «{f.status}»: {'; '.join(pendientes)}")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"bento: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
