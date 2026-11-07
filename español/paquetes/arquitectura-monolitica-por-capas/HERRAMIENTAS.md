# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/arquitectura-monolitica-por-capas`.

## `scripts/capas.py`

- `python3 $P/scripts/capas.py mapa`: módulos encontrados, sus capas y las del perfil que les faltan. Para orientarse antes de tocar nada.
- `python3 $P/scripts/capas.py revisar [RUTA…]`: imports que rompen las capas, los cruces o lo común, con `archivo:línea` y motivo. Sin rutas revisa todas las `raices`. Código 1 si hay infracciones.
- `python3 $P/scripts/capas.py iniciar`: crea `uxyngraphar/trabajo/arquitectura-monolitica-por-capas/ARQUITECTURA.md` desde la plantilla si falta.

## `scripts/verificar-capas.py`

Verificación del paquete (está en «verificaciones»). Revisa todo el código: con `nivel: aviso` lista las infracciones sin fallar; con `bloqueante`, falla si hay alguna.

## `scripts/capas_datos.py`

Librería compartida por los dos anteriores: lectura de ajustes, localización de módulo y capa de cada archivo, extracción de imports (JS/TS y Python) y motivo de cada infracción. No se ejecuta directamente.

## `scripts/comun/andamiar.py`

Crea un módulo con la estructura del perfil: `python3 $P/scripts/comun/andamiar.py modulo-servidor --nombre orders` simula; con `--aplicar` crea sin sobrescribir. Variantes: `modulo-servidor`, `modulo-cliente`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
