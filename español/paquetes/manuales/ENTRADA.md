# Manuales operativos — entrada

Activado con «usa el paquete manuales» / «sigue el protocolo runbook» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/manuales/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/manuales/REGLAS.md`.
3. Consulta manuales: `python3 $S/fichas.py listar manual`. Nuevo: `python3 $S/fichas.py nueva manual --slug <slug> --titulo "…"`.
4. Si tu cambio altera cómo se despliega, configura u opera algo, actualiza el manual afectado en la misma tarea.
5. Antes de terminar: `python3 $S/verificar.py`.

Trabajo: `uxyngraphar-work/manuales/`.
