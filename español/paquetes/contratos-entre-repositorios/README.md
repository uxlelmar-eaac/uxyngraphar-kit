# Contratos entre repositorios

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete contratos-entre-repositorios» / «sigue el protocolo contratos entre repositorios» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/contratos-entre-repositorios`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/identificar-contrato.md` → `$P/proceso/registrar-contrato.md` → `$P/proceso/sincronizar-repositorios.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/contratos-entre-repositorios/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-contratos.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## Para qué proyectos

Proyectos con un repositorio que sirve una API y otros que la consumen (servidor y cliente, o varios servicios). Cada repositorio instala el paquete y lleva sus propios contratos `CON-…`; los dos comparten el `id_compartido` de cada contrato. Guías de consulta: `referencia/sincronizar.md` (orden de merge y lista del PR) y `referencia/contratos-api.md` (lado técnico del consumidor).

## Lo que decide la persona

- Marcar un contrato `vigente` o `retirado`: `python3 $P/scripts/comun/fichas.py estado CON-… vigente --humano` (el agente deja `propuesto` o `deprecado`).
- Ajustes en `uxyngraphar/trabajo/contratos-entre-repositorios/ajustes.json`: `repo` (nombre de este repositorio) y `otros_repos` (rutas a los repositorios hermanos, p. ej. `["../mi-api"]`), que usan `contratos.py comparar` y `verificar-contratos.py`.
