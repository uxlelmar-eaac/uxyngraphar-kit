#!/usr/bin/env python3
"""Envío voluntario de sugerencias a quien mantiene uxyngraphar (solo las fichas EVO de 46-evolucion-documentacion).

Apagado por defecto. Solo lo activa una persona, nunca el agente (respondiendo Sí al instalar o actualizar, o con «activar»). Con el envío
activo, se envía al terminar un «instalar» o «actualizar» hecho por una persona, o con «enviar»; nunca desde CI, ganchos ni el agente.
Antes de activar, mira exactamente qué saldría con `previsualizar`. Guía: docs/10-guias/envio-sugerencias.md.

Uso:  python3 docs/scripts/feedback.py estado
      python3 docs/scripts/feedback.py previsualizar [--salida copia.json]   # qué se enviaría; no envía nada
      python3 docs/scripts/feedback.py activar --url https://… [--acepto]   # pide tu consentimiento
      python3 docs/scripts/feedback.py enviar [--todas]                     # envía lo nuevo o cambiado
      python3 docs/scripts/feedback.py revocar [--borrar-remoto]            # apaga el envío (y pide borrar lo enviado)
  Token opcional del servidor: variable UXYNGRAPHAR_FEEDBACK_TOKEN.
Salida: 0 · 1 si no hay nada que enviar · 2 si falta consentimiento o el envío falló.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "feedback"))
sys.path.insert(0, str(AQUI / "nucleo"))

import cliente  # noqa: E402
from terminal import hay_terminal  # noqa: E402
import lock  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402

AVISO = """Vas a activar el envío de sugerencias a quien mantiene uxyngraphar ({url}).

Qué se envía (al terminar un «instalar» o «actualizar» que hagas tú, o con «feedback.py enviar»):
  - Las fichas EVO de docs/46-evolucion-documentacion/ ({n} ahora): estado, tipo, impacto, prioridad,
    archivos del pack que proponen cambiar y su texto.
  - La versión y el tipo de pack, y un identificador aleatorio de esta instalación (sirve para pedir el borrado).
Qué se quita antes de enviar: el nombre del proyecto, los nombres de «feedback.ocultar» ({ocultar}), rutas de tu
equipo, correos, enlaces y cualquier línea que parezca una credencial. Nunca se envía código, historia de git, usuario,
nombre del equipo, ajustes locales ni métricas de uso. Nunca desde CI, ganchos ni el agente.
Puedes revocarlo cuando quieras («feedback.py revocar»). Revisa la copia exacta antes con «feedback.py previsualizar»."""


def _contexto(repo: Path, docs: str) -> tuple[dict, str, str]:
    cfg, problemas = cfgmod.cargar(repo, docs)
    errores = [p for p in problemas if p.startswith("feedback")]
    if errores:
        raise cliente.ErrorEnvio(errores[0])
    datos = lock.leer(repo, docs) or {}
    return cfg, datos.get("version") or lock.version_de(repo / docs), datos.get("pack") or lock.tipo_pack(repo / docs)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("orden", choices=("estado", "previsualizar", "activar", "enviar", "revocar"))
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--url", help=f"dirección del receptor (activar); por defecto la oficial: {cliente.URL_FEEDBACK_OFICIAL}")
    ap.add_argument("--acepto", action="store_true", help="activar sin preguntar (ya leíste qué se envía)")
    ap.add_argument("--todas", action="store_true", help="incluye también lo ya enviado y sin cambios")
    ap.add_argument("--salida", help="previsualizar: guarda la copia exacta en este archivo")
    ap.add_argument("--borrar-remoto", action="store_true", help="revocar: pide además al servidor que borre lo recibido")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    docs = repo / a.docs
    try:
        cfg, version, pack = _contexto(repo, a.docs)
        fb = cfg["feedback"]
        if a.orden == "estado":
            print(f"Envío de sugerencias: {'ACTIVO → ' + fb['url'] if fb['activo'] else 'apagado'}"
                  + (f" · consentimiento {fb['consentimiento']}" if fb["consentimiento"] else ""))
            print(f"Por enviar: {len(cliente.fichas(docs, repo.name, ocultar=tuple(fb['ocultar'])))} ficha(s) EVO nuevas o cambiadas.")
            return 0
        if a.orden == "previsualizar":
            _rutas, datos = cliente.paquete(docs, cfg, repo.name, version, pack, a.todas)
            texto = json.dumps(datos, ensure_ascii=False, indent=2)
            if a.salida:
                Path(a.salida).write_text(texto + "\n", encoding="utf-8", newline="\n")
                print(f"Copia exacta en {a.salida} ({len(datos['fichas'])} ficha(s) EVO). No se envió nada.")
            else:
                print(texto)
            return 0
        if a.orden == "activar":
            url = a.url or fb["url"] or cliente.URL_FEEDBACK_OFICIAL
            if not url or not cfgmod.url_permitida(url):
                raise cliente.ErrorEnvio("indica --url https://… (http solo hacia 127.0.0.1/localhost)")
            print(AVISO.format(url=url, ocultar=", ".join(fb["ocultar"]) or "ninguno", n=len(cliente.fichas(docs, repo.name, todas=True))))
            if not a.acepto:
                if not hay_terminal():
                    raise cliente.ErrorEnvio("sin terminal para preguntarte: vuelve a ejecutarlo en una terminal o añade --acepto")
                if input("\nEscribe «acepto» para activarlo: ").strip().lower() != "acepto":
                    print("No se activó nada.")
                    return 2
            hoy = date.today().isoformat()
            nuevo = {**fb, "activo": True, "url": url, "consentimiento": f"{hoy} ({cliente.TERMINOS})",
                     "id_instalacion": fb["id_instalacion"] or cliente.nuevo_id(), "respondido": "si", "respondido_en": hoy, "origen": "manual"}
            f = cliente.guardar_feedback(repo, a.docs, nuevo)
            print(f"Activado ({f.relative_to(repo).as_posix()}). Todavía no se envió nada: usa «feedback.py enviar».")
            return 0
        if a.orden == "revocar":
            if a.borrar_remoto and fb["id_instalacion"] and fb["url"]:
                cliente.borrar_remoto(fb["url"], fb["id_instalacion"], version)
                print("El servidor confirmó el borrado de lo recibido de esta instalación.")
            cliente.guardar_feedback(repo, a.docs, {**fb, "activo": False, "consentimiento": "", "respondido": "no",
                                                    "respondido_en": date.today().isoformat(), "origen": "manual",
                                                    "id_instalacion": "" if a.borrar_remoto else fb["id_instalacion"]})
            print("Envío apagado. No se enviará nada más.")
            return 0
        if not fb["activo"]:
            raise cliente.ErrorEnvio("el envío está apagado: revisa «feedback.py previsualizar» y actívalo con «feedback.py activar --url …»")
        rutas, datos = cliente.paquete(docs, cfg, repo.name, version, pack, a.todas)
        if not datos["fichas"] and not a.todas:
            print("Nada nuevo que enviar.")
            return 1
        respuesta = cliente.enviar(fb["url"], datos, version)
        cliente.marcar(rutas, datos)
        print(f"Enviadas {len(datos['fichas'])} ficha(s) EVO"
              + (f"; el servidor guardó {respuesta['guardadas']}" if isinstance(respuesta.get("guardadas"), int) else "") + ".")
        return 0
    except cliente.ErrorEnvio as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
