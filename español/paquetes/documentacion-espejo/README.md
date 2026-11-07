# Documentación espejo

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete documentacion-espejo» / «sigue el protocolo documentacion espejo» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/documentacion-espejo`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/leer-espejo.md` → `$P/proceso/actualizar-espejo.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/documentacion-espejo/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-espejo.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Cada archivo o carpeta relevante del código tiene un espejo en `uxyngraphar/trabajo/documentacion-espejo/` con la misma ruta: `src/orders/service.ts` → `…/src/orders/service.md`; `src/orders/` → `…/src/orders/README.md`. El espejo explica el papel del código; nunca lo copia.

## Lo que decide la persona

- Ajustes en `uxyngraphar/trabajo/documentacion-espejo/ajustes.json`: `raices` (carpetas de código espejadas), `extensiones`, `excluir` (globs) y `cobertura_minima` (porcentaje que exige `verificar-espejo.py`; por defecto 0).
- Qué cuenta como «lógica relevante» cuando hay dudas: el agente pregunta antes de espejar carpetas enteras.
