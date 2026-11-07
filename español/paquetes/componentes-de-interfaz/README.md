# Componentes de interfaz

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete componentes-de-interfaz» / «sigue el protocolo componentes de interfaz» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/componentes-de-interfaz`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/inventariar.md` → `$P/proceso/revisar.md` → `$P/proceso/corregir.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/componentes-de-interfaz/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

`uxyngraphar/trabajo/componentes-de-interfaz/INTERFAZ.md` guarda dónde están los tokens y componentes compartidos del proyecto y cada revisión de consistencia de las pantallas del pedido; solo se corrige lo que aprueba la persona.

## Lo que decide la persona

- Qué hallazgos se corrigen: marcar «sí» en la columna «Aprobada» de `INTERFAZ.md`.
- Qué hallazgos se aceptan sin corregir (estado `aceptado`, con la razón en «Notas»).
- Si se crea o cambia un token o un componente compartido, y cuál queda cuando dos sirven para lo mismo.
