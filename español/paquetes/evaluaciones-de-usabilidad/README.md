# Evaluaciones de usabilidad

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete evaluaciones-de-usabilidad» / «sigue el protocolo evaluaciones de usabilidad» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/evaluaciones-de-usabilidad`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/definir-alcance.md` → `$P/proceso/evaluar.md` → `$P/proceso/proponer.md` → `$P/proceso/implementar.md` → `$P/proceso/medir-resultado.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/evaluaciones-de-usabilidad/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-evaluaciones.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Cada mejora de interfaz pasa por una evaluación (ficha `UXE-…`): alcance y tareas del usuario, problemas con heurística, severidad y evidencia, propuesta, aprobación de una persona, implementación de lo aprobado y métricas antes/después.

## Lo que decide la persona

- Aprobar la propuesta: `python3 $P/scripts/comun/fichas.py estado UXE-… aprobada --humano` (y marcar «sí» en la columna «Aprobada» de cada fila que se implementa).
- Dar por buena la mejora tras medir: `python3 $P/scripts/comun/fichas.py estado UXE-… validada --humano`.
- Ajustes en `uxyngraphar/trabajo/evaluaciones-de-usabilidad/ajustes.json`: `heuristicas` (códigos admitidos), `severidad_max` y `severidad_propuesta_obligatoria` (desde qué severidad la propuesta es obligatoria; 3 por defecto).
- Si una métrica empeora tras implementar: seguir, revertir o aceptar la regresión.
