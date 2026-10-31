# Memoria del sistema
<!-- uxyngraphar:inicio -->

**Solo para personas (R-24).** Aquí terminan las fichas en lugar de borrarse: instrucciones, decisiones, auditorías, mejoras, evolución y herramientas que ya cumplieron su ciclo. Solo se añade; nada se edita.

- **El agente no la lee:** reglas `deny` de `.claude/settings.json`, `.cursorignore`, `.geminiignore` y `.aiexclude`, y las herramientas del pack la ignoran. La puerta (`controlar.py`) y el CI bloquean cualquier cambio hecho fuera de `memoria.py`.
- **Consultarla:** `python3 docs/scripts/memoria.py buscar TEXTO`, luego `ver ID`. Cada consulta queda en `registro-accesos.jsonl`.
- **Recuperar una ficha:** `memoria.py recuperar ID` (vuelve a `04-archivadas`).
- **Borrar de verdad** (solo un dato sensible): `memoria.py purgar ID --confirmar ID --motivo "…"`.

Estructura: `<sección>/<AAAA>/<AAAA-MM>/<ficha>.md` · `catalogo.jsonl` (un apunte por hecho, con la huella de cada ficha). Guía completa: [memoria.md](../10-guias/memoria.md).
<!-- uxyngraphar:fin -->
