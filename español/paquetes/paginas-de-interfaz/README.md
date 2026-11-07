# Páginas de interfaz

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete paginas-de-interfaz» / «sigue el protocolo paginas de interfaz» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/paginas-de-interfaz`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/consultar-ficha.md` → `$P/proceso/documentar-cambio.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/paginas-de-interfaz/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-paginas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## Dónde vive cada ficha

Una ficha `PAG-…` por ruta de interfaz, agrupada por módulo: `uxyngraphar/trabajo/paginas-de-interfaz/<modulo>/PAG-<fecha>-<ruta>.md`. `tipo`: `pagina`, `layout`, `modal-ruta` o `api-interna` (manejador de ruta del framework). Estados: `planificada`, `activa`, `deprecada` (con alternativa) y `retirada`.

## Lo que decide la persona

- Ajustes en `uxyngraphar/trabajo/paginas-de-interfaz/ajustes.json`: `campos_obligatorios` (por defecto `path`, `tipo`, `auth`) y `clave_unica` (por defecto `path`), que usa `verificar-paginas.py`.
- Qué ve el usuario en cada estado cuando el pedido no lo dice: el agente pregunta en lugar de inventarlo.
