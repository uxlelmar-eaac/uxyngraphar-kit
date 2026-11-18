# 0015 · Taller de sistemas de gobernanza (producto)

- **Estado:** aceptada
- **Fecha:** 2026-11-18
- **Sustituye en UX:** el Creador chat-first (panel y web)

## Contexto

El Creador priorizaba el chat de uxyn y un carril de validación. Quien adjuntaba un zip o una idea no veía los
archivos del sistema, el origen, ni cómo exportar/instalar. Había listas solapadas (Creador, catálogo local,
borradores web) y el puente kit↔nube quedaba en CLI.

## Decisión

1. **Metáfora:** el producto es un **taller**. El objeto principal es el **sistema** (carpeta de gobernanza), no el chat.
2. **uxyn es secundario:** propone cambios; la persona ve archivos, origen, estado de ciclo y acciones de salida sin abrir el chat.
3. **Ciclo de vida visible:** Idea/zip → Borrador → En este equipo → En un proyecto → Activo en el IDE (y opcionalmente Mercado).
4. **Navegación en cuatro áreas** (panel kit y web): **Taller**, **Proyectos**, **Mercado**, **Cuenta**.
5. **Layout del taller de un sistema:** archivos + editor por defecto; franja Origen; carril de ciclo; barra de salida siempre visible (Descargar, Sincronizar, Instalar, Publicar). uxyn es cajón o columna estrecha.
6. **Paridad kit ↔ web:** misma semántica de estado (`guidedState` / `creador-estado`); mismos CTAs de salida.

## Consecuencias

- El copy deja de decir que el editor es «solo para retoques».
- «Que uxyn complete» no es el único camino; el editor y la barra de salida lo son.
- El zip/idea es **origen** del sistema de gobernanza, no el entregable (no convierte el Creador en adaptador de PWA).
- Logs no compiten con el taller (Cuenta o cajón global).
