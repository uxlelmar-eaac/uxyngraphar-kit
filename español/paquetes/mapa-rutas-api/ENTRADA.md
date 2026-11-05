# Mapa de rutas de API — entrada

Activado con «usa el paquete mapa-rutas-api» / «sigue el protocolo endpoints» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/mapa-rutas-api/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/mapa-rutas-api/REGLAS.md`.
3. Antes de tocar un endpoint, lee su ficha: `python3 $S/fichas.py listar ruta` y `python3 $S/fichas.py ver <id>`.
4. Endpoint nuevo: `python3 $S/fichas.py nueva ruta --slug <metodo-ruta> --en <modulo> --titulo "GET /orders"`.
5. Al cambiar método, ruta, autenticación, entrada, salida o archivos, actualiza la ficha en la misma tarea. Endpoint eliminado: `fichas.py estado <id> retirada`.
6. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-rutas.py`.

Trabajo: `uxyngraphar-work/mapa-rutas-api/<modulo>/`.
