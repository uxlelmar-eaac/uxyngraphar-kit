# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/calidad-de-codigo`.

## `scripts/calidad.py`

Verificación del paquete (está en «verificaciones»).

- `python3 $P/scripts/calidad.py`: revisa todos los archivos de `raices` con alguna de las `extensiones` y fuera de `excluir`.
- `python3 $P/scripts/calidad.py <archivo>…`: revisa solo esos archivos (los que no tienen una extensión de código o están excluidos se ignoran).

Qué detecta: archivos con más de `limite_lineas` líneas físicas (salvo los de `exenciones_lineas`) y nombres de archivo con espacios. Imprime una línea por problema y un resumen; código 0 = sin problemas, 1 = hay problemas.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
