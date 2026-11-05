# Auditorías — entrada

Activado con «usa el paquete auditorias» / «sigue el protocolo auditoria» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/auditorias/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/auditorias/REGLAS.md`.
3. Abre la auditoría: `python3 $S/fichas.py nueva auditoria --slug <slug> --titulo "…"`; define alcance y preguntas **antes** de investigar. Pásala a `en-curso` al empezar.
4. Investiga solo dentro del alcance; cada hallazgo con evidencia (`ruta:línea`, comando, medición) y severidad.
5. Cierra con conclusiones y promociones propuestas; `fichas.py estado <id> cerrada`.
6. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-auditorias.py`.
