# Landing page bento — entrada

Activado con «usa el paquete landing-page-bento» / «sigue el protocolo bento» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/landing-page-bento/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/landing-page-bento/REGLAS.md` y, para diseñar, `guias/patrones-bento.md`.
3. Abre la ficha: `python3 $S/fichas.py nueva landing --slug <slug> --titulo "…"`. Rellena **Objetivo, Audiencia y Mosaico antes de escribir código**; pásala a `en-curso` al empezar a construir.
4. Construye siguiendo el mosaico de la ficha: si al construir cambia una celda, cambia primero la ficha.
5. Cuando esté lista, marca la checklist (`guias/checklist-publicacion.md` explica cada punto) y pásala a `revision`. Publicar (`publicada`) lo decide una persona.
6. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-bento.py`.
