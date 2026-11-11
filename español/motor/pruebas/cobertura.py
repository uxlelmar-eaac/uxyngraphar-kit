"""Suelo de cobertura del motor para CI (M-03): falla si el total del informe de coverage baja de SUELO.
Uso: python motor/pruebas/cobertura.py cobertura.txt"""

import re
import sys

SUELO = 69   # cobertura medida el 2026-11-10; se sube a medida que crecen las pruebas


def main(ruta: str) -> int:
    texto = open(ruta, encoding="utf-8").read()
    m = re.search(r"^TOTAL\s.*?(\d+)%\s*$", texto, re.M)
    if not m:
        print("no encuentro la línea TOTAL en el informe")
        return 2
    total = int(m.group(1))
    print(f"cobertura total {total}% (suelo {SUELO}%)")
    return 0 if total >= SUELO else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
