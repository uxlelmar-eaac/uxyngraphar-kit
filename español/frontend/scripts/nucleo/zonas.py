"""Zonas del pack dentro de archivos mixtos (clase M: README.md, INDICE.md).

Un archivo mixto mezcla texto del pack con filas o notas del proyecto. El pack marca lo suyo así:

    <!-- uxyngraphar:inicio -->
    …texto que mantiene el pack…
    <!-- uxyngraphar:fin -->

Al actualizar solo se reescribe lo que está entre marcadores (zona por zona, en orden); lo de fuera es del proyecto y no se toca.
Si el archivo local no tiene marcadores, o tiene un número distinto de zonas que el pack, no se fusiona: se avisa para revisarlo a mano.
"""

from __future__ import annotations

import re

INICIO = "<!-- uxyngraphar:inicio -->"
FIN = "<!-- uxyngraphar:fin -->"
_ZONA = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIN), re.S)


def zonas(texto: str) -> list[str]:
    return _ZONA.findall(texto)


def fusionar(local: str, nuevo: str) -> str | None:
    """Texto local con las zonas del pack sustituidas por las del pack nuevo. None si no se puede fusionar con seguridad."""
    z_local, z_nuevo = zonas(local), zonas(nuevo)
    if not z_local or len(z_local) != len(z_nuevo):
        return None
    pendientes = iter(z_nuevo)
    return _ZONA.sub(lambda _m: next(pendientes), local)
