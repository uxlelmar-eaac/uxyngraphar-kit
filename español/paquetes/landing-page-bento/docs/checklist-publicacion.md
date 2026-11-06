# Checklist de publicación — cómo comprobar cada punto

| Punto | Cómo se comprueba |
|-------|-------------------|
| Contraste AA | Texto normal ≥ 4.5:1, texto grande y controles ≥ 3:1 (herramienta de contraste del navegador o Lighthouse). |
| Foco visible y orden | Recorre la página con Tab: el foco se ve siempre y sigue la prioridad del mosaico. |
| Texto alternativo | Toda `img` informativa con `alt` descriptivo; decorativas con `alt=""` o `aria-hidden`. |
| prefers-reduced-motion | Activa «reducir movimiento» en el sistema: no quedan animaciones de desplazamiento ni paralaje. |
| Carga prioritaria | La imagen protagonista con prioridad (p. ej. `fetchpriority="high"` o la opción del framework); el resto `loading="lazy"`. |
| Sin saltos de diseño | Medios con `width`/`height` o `aspect-ratio`; CLS < 0.1 en Lighthouse. |
| Tres tamaños | Móvil (~375 px), tableta (~768 px) y escritorio (≥ 1280 px); el apilado móvil sigue la prioridad. |
| CTA primario | Se pulsa, llega a su destino y tiene nombre accesible. |

Marca cada casilla en la ficha (`- [x]`) solo después de comprobarla. Si un punto no aplica, márcalo y explica por qué en Notas.
