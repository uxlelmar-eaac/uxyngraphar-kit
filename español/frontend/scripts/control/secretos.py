"""Detección de credenciales (R-12): por contenido (líneas) y por nombre de archivo. Sin dependencias.

Los hallazgos nunca incluyen el valor completo (se enmascara). Falsos positivos: placeholders conocidos se
ignoran; una línea con la marca `uxyngraphar:permitir-secreto` queda exenta (para fixtures de pruebas).
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

MARCA_PERMITIR = "uxyngraphar:permitir-secreto"
PATRONES = [
    ("clave AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("clave privada", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY")),
    ("token GitHub", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    ("token Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("clave API (sk-)", re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b")),
    ("clave Stripe", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{16,}\b")),
    ("clave Google", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("URL con credenciales", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@\"']{2,}:[^\s/@\"']{4,}@[^\s/\"']+")),
    ("token npm/registro", re.compile(r"_auth(?:Token)?\s*=\s*[A-Za-z0-9+/=_-]{16,}")),
    ("credencial asignada", re.compile(r"""(?i)\b(?:password|passwd|pwd|secret|client_secret|api[_-]?key|access[_-]?key|auth[_-]?token|token)\b["']?\s*[:=]\s*["'][^"'\s${}<>]{8,}["']""")),
]
PLACEHOLDER = re.compile(r"(?i)example|changeme|cambiar|placeholder|xxxx|your[_-]|<[^>]+>|dummy|fake|\*{4}|\$\{|%\(|process\.env|os\.environ|getenv|secrets\.|redacted|\bfoo\b|\bbar\b|user:pass|usuario:contra")
# Archivos que no deben versionarse: por nombre (glob sobre ruta o nombre base).
ARCHIVOS_PROHIBIDOS = [
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore", "id_rsa", "id_rsa.*", "id_dsa", "id_ecdsa", "id_ed25519",
    "credentials.json", "service-account*.json", "*-credentials.json", ".netrc", ".npmrc", ".pypirc", "*.kdbx", "*.tfstate", "*.tfstate.*",
    "terraform.tfvars", "secrets.yml", "secrets.yaml", "secrets.json", ".htpasswd", "*.ovpn",
]
# Plantillas sin valores reales: permitidas aunque coincidan.
ARCHIVOS_PERMITIDOS = [".env.example", ".env.sample", ".env.template", ".env.dist", "*.example", "*.sample", "*.template", "*.pub"]


# Patrones débiles (heurística por nombre de variable): en archivos de prueba son casi siempre datos falsos, así que ahí no se avisa.
# Los patrones fuertes (claves AWS/GitHub/Stripe…, llaves privadas, JWT) se siguen detectando en cualquier ruta.
DEBILES = {"credencial asignada"}
RUTA_PRUEBA = re.compile(r"(?i)(^|/)(tests?|__tests__|__mocks__|spec|e2e|fixtures?|mocks?|testdata|cypress)/|\.(spec|test|e2e-spec|e2e|stories)\.[a-z0-9]+$|(^|/)(test_[^/]*|[^/]*_test)\.(py|go|rb)$|(^|/)conftest\.py$")


def es_ruta_de_prueba(ruta: str) -> bool:
    return bool(RUTA_PRUEBA.search(ruta.replace("\\", "/")))


@dataclass
class Hallazgo:
    ruta: str
    linea: int
    tipo: str
    muestra: str


def enmascarar(valor: str) -> str:
    v = valor.strip()
    return v[:4] + "…" + f"({len(v)} car.)" if len(v) > 8 else "…"


def en_linea(linea: str, ruta: str = "") -> tuple[str, str] | None:
    if MARCA_PERMITIR in linea or PLACEHOLDER.search(linea):
        return None
    prueba = bool(ruta) and es_ruta_de_prueba(ruta)
    for tipo, rx in PATRONES:
        if prueba and tipo in DEBILES:
            continue
        m = rx.search(linea)
        if m:
            return tipo, enmascarar(m.group(0))
    return None


def escanear_texto(ruta: str, texto: str) -> list[Hallazgo]:
    salida = []
    for n, linea in enumerate(texto.splitlines(), 1):
        r = en_linea(linea, ruta)
        if r:
            salida.append(Hallazgo(ruta, n, *r))
    return salida


def _coincide(ruta: str, patrones: list[str]) -> bool:
    nombre = Path(ruta).name
    return any(fnmatch.fnmatch(nombre, p) or fnmatch.fnmatch(ruta, p) for p in patrones)


def archivo_prohibido(ruta: str) -> bool:
    ruta = ruta.replace("\\", "/")
    return _coincide(ruta, ARCHIVOS_PROHIBIDOS) and not _coincide(ruta, ARCHIVOS_PERMITIDOS)
