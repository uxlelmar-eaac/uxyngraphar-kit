# Documentación espejo

Mantiene un espejo por archivo o carpeta relevante del código —rol, responsabilidades, interacciones y puntos de extensión— en la misma ruta dentro del trabajo del paquete, con cobertura medible y sin espejos huérfanos.

## Qué resuelve

Para cambiar un archivo hay que saber qué papel tiene, quién lo usa y dónde se extiende; leerlo entero cada vez es caro para una persona y para un agente. Los comentarios se pierden y los documentos sueltos se desfasan porque nadie sabe dónde están. Este paquete fija un sitio predecible para esa explicación (la ruta del código, en espejo), mide cuánto código la tiene y detecta los espejos que quedaron sin código.

## Problemas que cubre

- `codigo-sin-espejo`: archivos o carpetas relevantes sin espejo, o cobertura bajo el mínimo.
- `espejos-huerfanos`: espejos cuyo código ya no existe.
- `espejos-desfasados`: espejos que no reflejan el rol o las interacciones actuales.
- `espejos-que-copian-codigo`: espejos que pegan o parafrasean el código en lugar de explicar su papel.

## Fuera de alcance

- Áreas funcionales, sus fronteras y su mapa de lectura: `mapa-de-modulos`.
- El contrato de cada endpoint: `rutas-de-api`.
- Cada página o ruta de la interfaz: `paginas-de-interfaz`.
- Imports entre capas de un módulo: `arquitectura-monolitica-por-capas`.
- Comentarios dentro del código y documentación pública para usuarios externos: no lo cubre el kit.

## Cuándo usarlo

- Antes de cambiar código que no conoces: se lee su espejo primero.
- Al crear, mover, renombrar o borrar un archivo o carpeta relevante.
- Al cambiar la responsabilidad o las interacciones de un archivo.
- Al adoptar el paquete en un proyecto existente (mapa de cobertura y espejado por módulos).

## Cuándo no usarlo

- En repositorios pequeños donde leer el código es más rápido que mantener su espejo.
- Para código generado, pruebas o tipos triviales.

## Entradas y salidas

- Entradas: el código bajo `raices` (por defecto `src/`) y los ajustes `extensiones`, `excluir` y `cobertura_minima`.
- Salidas: espejos `.md` (archivos) y `README.md` (carpetas) en `uxyngraphar/trabajo/documentacion-espejo/<ruta-del-codigo>`, el mapa de cobertura de `espejo.py mapa` y el informe de `verificar-espejo.py`.

## Paquetes complementarios

- `mapa-de-modulos`: el contexto del área dice qué leer; el espejo explica cada pieza.
- `arquitectura-monolitica-por-capas`: los módulos nuevos que crea se espejan aquí.
- `verificaciones-vivas`: contrasta la documentación con el código bajo pedido.
