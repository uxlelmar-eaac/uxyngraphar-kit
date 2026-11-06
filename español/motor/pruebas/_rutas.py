"""Pone el motor y la migración en sys.path para las pruebas (importar antes que cualquier módulo del motor)."""

import sys
from pathlib import Path

sys.dont_write_bytecode = True
ES = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ES / "motor"), str(ES / "motor" / "migracion")]
