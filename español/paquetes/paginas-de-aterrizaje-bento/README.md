# Páginas de aterrizaje bento

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete paginas-de-aterrizaje-bento» / «sigue el protocolo paginas de aterrizaje bento» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/paginas-de-aterrizaje-bento`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/redactar-brief.md` → `$P/proceso/disenar-mosaico.md` → `$P/proceso/construir.md` → `$P/proceso/revisar-publicacion.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/paginas-de-aterrizaje-bento/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-bento.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Cada página de aterrizaje nace de una ficha `LAN-…` con objetivo, audiencia y mosaico (celdas con tamaño, prioridad, título, mensaje, CTA y medio); el código sigue a la ficha y `verificar-bento.py` comprueba el mosaico y la checklist de publicación.

## Lo que decide la persona

- Publicar: `python3 $P/scripts/comun/fichas.py estado LAN-… publicada --humano`, después de revisar la página en `revision`.
- Ajustes en `uxyngraphar/trabajo/paginas-de-aterrizaje-bento/ajustes.json`: `columnas` (4), `tamanos` permitidos, `celdas_min` y `celdas_max` (5–9), `max_2x2` (1), `palabras_titulo` (6) y `palabras_mensaje` (25).
- El objetivo de la página y su CTA principal, si el pedido no los deja claros.
