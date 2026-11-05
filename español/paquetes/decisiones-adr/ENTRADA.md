# Decisiones de arquitectura (ADR) — entrada

Activado con «usa el paquete decisiones-adr» / «sigue el protocolo adr» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/decisiones-adr/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/decisiones-adr/REGLAS.md`.
3. Antes de decidir algo estructural, consulta las ADR vigentes: `python3 $S/fichas.py listar adr --status aceptada`.
4. Nueva decisión: `python3 $S/fichas.py nueva adr --slug <slug> --titulo "…"`; complétala y pásala a `en-evaluacion` cuando esté lista para la persona.
5. Antes de terminar: `python3 $S/verificar.py`.

Trabajo: `uxyngraphar-work/decisiones-adr/<estado>/`.
