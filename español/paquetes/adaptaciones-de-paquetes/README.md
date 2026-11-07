# Adaptaciones de paquetes

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete adaptaciones-de-paquetes» / «sigue el protocolo adaptaciones de paquetes» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/adaptaciones-de-paquetes`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/consultar-ajustes.md` → `$P/proceso/seguir-ajustes.md` → `$P/proceso/proponer-ajuste.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/adaptaciones-de-paquetes/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-adaptaciones.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Lo que un paquete inmutable no encaja en este proyecto se adapta con un ajuste local (`AJL-*`) que una persona aprueba, sin editar el paquete; si el paquete cambia, el ajuste queda «por revisar».

## Lo que decide la persona

- Activar o revisar un ajuste local: `python3 $P/scripts/adaptaciones.py aprobar-ajuste AJL-… --humano` (guarda la huella del archivo que complementa).
- Retirarlo: `python3 $P/scripts/comun/fichas.py estado AJL-… retirado --humano`.

Al activar cualquier otro paquete, el agente ejecuta `python3 $P/scripts/adaptaciones.py ajustes <id>` (`al_activar_paquete`) y sigue los ajustes locales activos que imprima.
