# Plantilla — revisar y aprobar mejora propuesta (cliente)

Checklist humano cuando una ficha en `45-mejoras-propuestas/` debe pasar a trabajo ejecutable.

## Cuándo usar

La IA registró deuda/mejora fuera de alcance y el equipo decide abordarla.

## Checklist

1. [ ] Leer ficha en `45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/<slug>.md` y validar evidencia.
2. [ ] Enriquecer sección **Notas del humano** (prioridad, restricciones, contexto negocio).
3. [ ] Decidir:
   - **Aprobar** → continuar paso 4 (mover a `02-en-progreso/`)
   - **Posponer** → dejar `pending` en `01-pendientes/`
   - **Rechazar** → `status: rejected`; mover a `05-canceladas/`
4. [ ] Crear instrucción en `05-instrucciones/01-pendientes/YYYY-MM-DD/` desde [_PLANTILLA.md](../05-instrucciones/_PLANTILLA.md):
   - Pedido derivado de la ficha de mejora (alcance UI acotado)
   - Enlazar `related_mejora: MEJ-...` en frontmatter (opcional)
   - Alcance acotado; no arrastrar otras mejoras pendientes
5. [ ] Marcar mejora `status: approved` y campo `instruction_derivada: YYYYMMDD-NNN` (+ `02-en-progreso/`).
6. [ ] Aprobar instrucción nueva → ejecutar en sesión aparte.

## No hacer

- Implementar la mejora sin instrucción `approved` nueva.
- Mezclar varias propuestas en una sola instrucción sin acuerdo explícito.
- Borrar la ficha origen (historial de por qué se detectó).

## Referencias

- [mejoras-propuestas-ia.md](../10-guias/mejoras-propuestas-ia.md)
- [_PROTOCOLO.md](_PROTOCOLO.md)
