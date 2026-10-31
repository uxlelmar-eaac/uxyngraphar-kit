---
id: auto.05.estados-con-fecha
stack: [servidor]
---

# 05: estados-con-fecha

## Fuente

Carpetas con estados (`05-instrucciones`, `20-decisiones`, `40-auditorias`,
`45-mejoras-propuestas`, `46-evolucion-documentacion`) y
`scripts/validar-documentacion.py` (flags `STRICT_*`, `DECISIONES_MAX_DAYS`).

## Valida

Que nada con fecha o antigüedad máxima quede estancado sin reporte.

## Procedimiento

1. Correr `python3 scripts/validar-documentacion.py` con los flags estrictos del proyecto.
2. Listar fichas vencidas o más viejas que el máximo permitido.

## Aceptación

- [ ] El script de validación pasa en verde.
- [ ] Cero fichas vencidas sin reporte explícito.

## Salida

La del script + lista de `ficha | estado | días | responsable`.
