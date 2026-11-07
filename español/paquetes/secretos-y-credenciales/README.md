# Secretos y credenciales

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete secretos-y-credenciales» / «sigue el protocolo secretos y credenciales» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/secretos-y-credenciales`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/diagnosticar.md` → `$P/proceso/implementar.md` → `$P/proceso/escanear.md` → `$P/proceso/atender-incidente.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/secretos-y-credenciales/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/secretos.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Ningún valor sensible entra al repositorio: en el código solo hay `<PLACEHOLDER>` o variables de entorno, los archivos de secretos no se leen ni se versionan y `secretos.py` lo comprueba por contenido y por nombre de archivo, mostrando siempre los valores enmascarados.

## Lo que decide la persona

- Ajustes en `uxyngraphar/trabajo/secretos-y-credenciales/ajustes.json`: `raices`, `excluir`, `permitir` (globs de rutas exentas, por ejemplo fixtures ficticios) y `max_kb`.
- Cuándo se puede usar la marca `uxyngraphar:permitir-secreto` en una línea de datos de prueba.
- Ante un secreto real expuesto: revocarlo en el proveedor, emitir uno nuevo y, si llegó a un remoto, limpiar el historial (`referencia/si-aparece-un-secreto.md`).
