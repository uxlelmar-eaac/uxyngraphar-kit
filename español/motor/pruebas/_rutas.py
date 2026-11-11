"""Pone el motor en sys.path para las pruebas (importar antes que cualquier módulo del motor) y aísla la
carpeta de uxyngraphar: las pruebas nunca leen ni escriben la casa real de la persona (panel.json, respaldos…)."""

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
MOTOR = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(MOTOR)]

if "UXYNGRAPHAR_HOME" not in os.environ:
    CASA_PRUEBAS = tempfile.mkdtemp(prefix="uxy-casa-pruebas-")
    os.environ["UXYNGRAPHAR_HOME"] = CASA_PRUEBAS
    atexit.register(shutil.rmtree, CASA_PRUEBAS, True)

# Las pruebas no usan el servidor de sistemas de gobernanza salvo que lo pidan (test_remoto levanta uno falso).
os.environ.setdefault("UXYNGRAPHAR_SIN_RED", "1")
