# Mejoras pendientes — entrada

Activado con «usa el paquete mejoras-pendientes» / «sigue el protocolo mejoras» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/mejoras-pendientes/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/mejoras-pendientes/REGLAS.md`.
3. Si durante una tarea detectas deuda o un bug fuera de alcance: `python3 $S/fichas.py nueva mejora --slug <slug> --titulo "…"` con evidencia. **No lo implementes.**
4. Antes de registrar, revisa duplicados: `python3 $S/fichas.py listar mejora --status pending`.
5. Antes de terminar: `python3 $S/verificar.py`.
