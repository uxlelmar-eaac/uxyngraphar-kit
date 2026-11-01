# Aprobar instrucciones

Sin instrucción **aprobada**, el agente no debe editar código ni documentación de producto.

## Cómo se aprueba

1. Abre el panel: `uxyngraphar`.
2. **Mis proyectos** → «Abrir» en el proyecto → **Pendientes** (el número junto a la pestaña es lo que espera tu decisión).
3. «Leer y decidir»: lee la ficha entera.
4. Elige (Aprobar, Cancelar, Posponer… según el tipo) y mira **exactamente qué cambia** en la ficha.
5. «Confirmar». La ficha pasa a su carpeta de estado (aprobada → `02-en-progreso/`) y queda una copia de la anterior en **Copias de seguridad** por si te equivocas.
6. Haz commit del cambio.

Lo mismo vale para mejoras (45), cambios al pack (EVO, 46), propuestas de herramientas, ADR y auditorías. Si una instrucción pide más de 5 archivos de código (R-21), el panel muestra su justificación antes de que decidas.

## Qué revisas tú

- Objetivo claro y acotado
- Anclas de código/docs correctas
- Que no pida tocar el núcleo del pack
- Que quepa en los límites (archivos/líneas)

## Dónde viven

`uxyngraphar/05-instrucciones/` con carpetas por estado/fecha (ver `organizacion-estados-fechas.md` en guías).

## Consejo

Prefiere varias instrucciones pequeñas a una gigante.

## Avanzado (terminal)

`python3 uxyngraphar/scripts/decisiones/decisiones.py scan`, `register --id ID --action aprobar` y `apply`: ver `uxyngraphar/35-herramientas/autorizadas/decisiones-pendientes.md`.
