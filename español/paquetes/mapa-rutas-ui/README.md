# Mapa de rutas de interfaz — entrada

Activado con «usa el paquete mapa-rutas-ui» / «sigue el protocolo paginas» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/mapa-rutas-ui/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/mapa-rutas-ui/REGLAS.md`.
3. Antes de tocar una página, lee su ficha: `python3 $S/fichas.py listar ruta` y `python3 $S/fichas.py ver <id>`.
4. Página nueva: `python3 $S/fichas.py nueva ruta --slug <ruta> --en <modulo> --titulo "/checkout"`.
5. Al cambiar ruta, acceso, datos, estados o componentes principales, actualiza la ficha en la misma tarea. Página eliminada: `fichas.py estado <id> retirada`.
6. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-rutas.py`.

Trabajo: `uxyngraphar-work/mapa-rutas-ui/<modulo>/`.
