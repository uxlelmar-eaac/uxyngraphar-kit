# Áreas y módulos — entrada

Activado con «usa el paquete areas-modulos» / «sigue el protocolo areas» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/areas-modulos/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/areas-modulos/REGLAS.md`.
3. Antes de cambiar algo, identifica el área: `python3 $S/fichas.py listar area` y lee su contexto (`fichas.py ver <id>`); sigue su «Mapa de lectura».
4. Área nueva: `python3 $S/fichas.py nueva area --slug <area> --en <area> --titulo "Área: …"`.
5. Si cambias fronteras, dependencias o código ancla de un área, actualiza su contexto en la misma tarea.
6. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-areas.py`.

Trabajo: `uxyngraphar-work/areas-modulos/<area>/`.
