# Documentos archivados

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete documentos-archivados» / «sigue el protocolo documentos archivados» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/documentos-archivados`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/archivar-documento.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/ejemplos/` (casos resueltos).
7. Trabajo: escribe solo en `uxyngraphar/trabajo/documentos-archivados/` y, en el código del proyecto, solo lo que el pedido pida.
8. Antes de terminar: `python3 $P/scripts/comun/verificar.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## Dónde vive el archivo

`uxyngraphar/trabajo/documentos-archivados/archivo/<AAAA-MM-DD>/`: copias fechadas de documentos retirados. Solo se añade; el agente no lo lee nunca (está en `fuera_de_ia` y en `protegidos`).

## Lo que decide la persona

- Archivar un documento: `python3 $P/scripts/archivo.py archivar <ruta> --humano`.
- Consultar el archivo: `python3 $P/scripts/archivo.py buscar <texto> --humano`. Si algo del archivo vuelve a importar, la persona lo trae como nota con `notas-de-memoria`.
