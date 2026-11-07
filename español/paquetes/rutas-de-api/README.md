# Rutas de API

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete rutas-de-api» / «sigue el protocolo rutas de api» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/rutas-de-api`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/consultar-ficha.md` → `$P/proceso/documentar-cambio.md` → `$P/proceso/verificar.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/rutas-de-api/` (fichas con `python3 $P/scripts/comun/fichas.py …`) y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-rutas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## Dónde vive cada ficha

Una ficha `RUT-…` por endpoint, agrupada por módulo: `uxyngraphar/trabajo/rutas-de-api/<modulo>/RUT-<fecha>-<metodo-ruta>.md`. Estados: `planificada` (aún no existe en el código), `activa`, `deprecada` (sigue respondiendo; la ficha dice la alternativa) y `retirada` (ya no existe).

## Lo que decide la persona

- Ajustes en `uxyngraphar/trabajo/rutas-de-api/ajustes.json`: `campos_obligatorios` (por defecto `method`, `path`, `auth`) y `clave_unica` (por defecto `method` + `path`), que usa `verificar-rutas.py`.
- Qué endpoints son públicos: el agente declara `auth: public` solo si el pedido lo dice y lo justifica en «Hace».
