"""Pone el motor y la migración en sys.path para las pruebas (importar antes que cualquier módulo del motor)."""

import sys
from pathlib import Path

sys.dont_write_bytecode = True
MOTOR = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(MOTOR), str(MOTOR / "migracion")]
