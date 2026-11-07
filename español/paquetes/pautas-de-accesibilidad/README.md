# Pautas de accesibilidad

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete pautas-de-accesibilidad» / «sigue el protocolo pautas de accesibilidad» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/pautas-de-accesibilidad`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/revisar.md` → `$P/proceso/corregir.md` → `$P/proceso/comprobar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/pautas-de-accesibilidad/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Cada revisión deja en `uxyngraphar/trabajo/pautas-de-accesibilidad/ACCESIBILIDAD.md` las barreras de las pantallas del pedido con su criterio WCAG 2.2 AA y su evidencia; solo se corrige lo que aprueba la persona y se comprueba con la misma herramienta.

## Lo que decide la persona

- Qué barreras se corrigen: marcar «sí» en la columna «Aprobada» de `ACCESIBILIDAD.md`.
- Qué barreras se aceptan sin corregir (estado `aceptada`, con la razón en «Notas»).
- Si una corrección exige cambiar un token o un componente compartido.
