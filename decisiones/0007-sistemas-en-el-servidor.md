# 0007 · Los sistemas de gobernanza viven en el servidor; el instalador llega vacío

- **Estado:** aceptada
- **Fecha:** 2026-11-11
- **Plan:** `PLAN-SISTEMAS-DE-GOBERNANZA.md` (raíz de uxyngraphar), fases 2 y 4

## Contexto

Si el zip de la herramienta trajera todo el catálogo, para tener un sistema nuevo o una corrección habría que
publicar una versión entera de la herramienta, y no habría forma de que otras personas aportaran sistemas. El objetivo
es poder descargar, subir, compartir y, más adelante, vender los **sistemas de gobernanza**.

## Decisión

1. **El instalador llega vacío.** El zip de la herramienta lleva `motor/` y `sistemas-de-gobernanza/_base/` (protocolo y
   `scripts/comun/`). Ningún sistema.
2. **El servidor es la fuente de los sistemas** (`/v1/sistemas` del backend de uxyngraphar). El motor lo consulta con
   `remoto.py` (solo biblioteca estándar, ADR 0001): índice con ETag, búsqueda, ficha, descarga y publicación.
3. **Caché local** en `~/.uxyngraphar/sistemas-de-gobernanza/<editor>/<id>/<version>/`: lo traído se comprueba (sha256
   del índice + INTEGRIDAD.json), queda en solo lectura y sirve sin red. El índice guardado permite buscar sin red.
4. **Catálogo local opcional** para quien escribe sistemas (`UXYNGRAPHAR_CATALOGO`, `catalogo_local` en `casa.json`, o
   el `sistemas-de-gobernanza/` del repo del kit). `fuentes.py` une local y servidor: gana la versión más alta y, a
   igual versión, la local.
5. **Instalar no cambia para el proyecto**: sigue copiando la construcción en `uxyngraphar/sistemas-de-gobernanza/<id>/`
   dentro de una transacción. Los proyectos no dependen de la red una vez instalados (ADR 0003).
6. **Paso intermedio:** las fuentes de los sistemas propios siguen en este repo (`español/sistemas-de-gobernanza/`) y
   se publican con `uxyngraphar publicar` o `publicar.py --artefactos`. Moverlas a un repo propio queda para cuando
   exista.

## Consecuencias

- Sin red y sin caché no se puede instalar un sistema nuevo; lo ya instalado sigue funcionando.
- `UXYNGRAPHAR_SIN_RED=1` apaga el servidor (pruebas, equipos aislados). `UXYNGRAPHAR_SERVIDOR` cambia la URL; solo se
  acepta https (o http en 127.0.0.1 para pruebas).
- Publicar exige un token de publicación (`uxyngraphar sesion guardar`), emitido por el panel ROOT del backend.
