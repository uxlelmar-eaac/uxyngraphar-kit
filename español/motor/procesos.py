"""¿Sigue vivo un proceso? Igual en Linux, macOS y Windows. Lo usan el panel (un solo panel por equipo) y el candado
de cada proyecto (`transaccion.candado`)."""

from __future__ import annotations

import os
import subprocess

# Procesos lanzados por este proceso: se consultan con poll(), que además los recoge al terminar.
LANZADOS: dict[int, subprocess.Popen] = {}


def _vivo_windows(pid: int) -> bool:
    """En Windows `os.kill(pid, 0)` no comprueba nada: 0 es CTRL_C_EVENT y manda Ctrl+C al grupo de procesos `pid`."""
    import ctypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]  # solo existe en Windows
    kernel32.OpenProcess.restype = ctypes.c_void_p
    manejador = kernel32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
    if not manejador:
        return ctypes.get_last_error() == 5  # type: ignore[attr-defined]  # solo existe en Windows   # acceso denegado: existe, pero es de otro usuario
    try:
        codigo = ctypes.c_ulong()
        if not kernel32.GetExitCodeProcess(ctypes.c_void_p(manejador), ctypes.byref(codigo)):
            return False
        return codigo.value == 259   # STILL_ACTIVE
    finally:
        kernel32.CloseHandle(ctypes.c_void_p(manejador))


def vivo(pid) -> bool:
    """True si el proceso `pid` sigue en marcha. Un pid ausente, no numérico o <= 0 nunca está vivo (en POSIX
    `kill(0, 0)` se refiere al propio grupo de procesos)."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0 or pid > 2 ** 31 - 1:
        return False
    propio = LANZADOS.get(pid)
    if propio is not None:
        return propio.poll() is None
    if os.name == "nt":
        try:
            return _vivo_windows(pid)
        except (OSError, AttributeError):
            return False
    try:
        if os.waitpid(pid, os.WNOHANG)[0] == pid:   # un hijo de este proceso que ya terminó
            return False
    except ChildProcessError:
        pass
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True    # existe, pero es de otro usuario
    except OSError:
        return False
    return True

