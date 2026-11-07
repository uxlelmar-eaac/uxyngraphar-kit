# Idiomas del código

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete idiomas-del-codigo» / «sigue el protocolo idiomas del codigo» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/idiomas-del-codigo`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/diagnosticar.md` → `$P/proceso/escribir-codigo.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/idiomas-del-codigo/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/idiomas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Todo artefacto de código va en inglés ASCII (la conversación, en el idioma de la persona); solo los términos de dominio del glosario quedan sin traducir y el texto para el usuario va por i18n. `idiomas.py` comprueba los nombres de archivo sin IA.

## Lo que decide la persona

- El glosario de dominio `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md`: `python3 $P/scripts/glosario.py iniciar` lo crea vacío; solo una persona añade términos (la IA no puede editarlo).
- Ajustes en `uxyngraphar/trabajo/idiomas-del-codigo/ajustes.json`: `raices`, `extensiones` y `excluir`.
- El renombrado de código antiguo en otro idioma.

Que los nombres se expliquen solos está en `calidad-de-codigo`; el idioma de los commits, en `mensajes-de-commit`.
