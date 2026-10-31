"""¿Hay una persona en la terminal? (las acciones que solo puede hacer una persona: memoria, respaldos, activar el envío…).

`sys.stdin.isatty()` no basta en Windows: el dispositivo NUL (entrada redirigida a «nada», como hacen el CI, los agentes y
`subprocess.DEVNULL`) también responde True. Allí se pregunta a la consola de verdad con GetConsoleMode.
Solo stdlib.
"""

from __future__ import annotations

import os
import sys
from typing import IO


def hay_terminal(flujo: IO | None = None) -> bool:
    flujo = sys.stdin if flujo is None else flujo
    try:
        if not flujo.isatty():
            return False
        if os.name != "nt":
            return True
        import ctypes
        import msvcrt
        modo = ctypes.c_uint32()
        return bool(ctypes.windll.kernel32.GetConsoleMode(msvcrt.get_osfhandle(flujo.fileno()), ctypes.byref(modo)))
    except (AttributeError, OSError, ValueError):
        return False
