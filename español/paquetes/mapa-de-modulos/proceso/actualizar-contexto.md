---
fase: actualizar-contexto
resuelve: [fronteras-de-area-difusas, contextos-de-area-desfasados, dependencias-hacia-areas-sin-documentar]
skills: [documentar-area]
---

# Fase: actualizar-contexto

## Objetivo

Solo si el cambio crea un área o altera sus fronteras, dependencias o código ancla: que el contexto describa el área tal como queda.

## Entradas

- El área o áreas de `identificar-area`.
- El código tras el cambio.

## Pasos

1. Área nueva → skill `documentar-area`.
2. Área existente: edita su contexto en `uxyngraphar/trabajo/mapa-de-modulos/<area>/`:
   - «Fronteras»: lo que pasa a poseer o deja de poseer, tablas nuevas, externos nuevos.
   - `depends_on`: añade o quita nombres de área (carpetas). Si la dependencia nueva apunta a un área sin contexto, documéntala o avisa al cerrar.
   - «Código ancla»: rutas nuevas si el código se movió.
   - «Mapa de lectura»: ajústalo si cambió el punto de entrada; máximo cinco pasos.
3. Si una responsabilidad pasa de un área a otra, actualiza las dos («Posee» en una, «No posee» en la otra).
4. Actualiza `fecha`.

## Criterio de salida

- Las fronteras, `depends_on` y anclas del contexto coinciden con el código.
- Ninguna responsabilidad aparece en «Posee» de dos áreas.
