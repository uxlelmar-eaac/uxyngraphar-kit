---
fase: concluir
resuelve: [conclusiones-sin-seguimiento, investigaciones-sin-alcance]
skills: []
---

# Fase: concluir

## Objetivo

Cerrar la auditoría con respuestas a las preguntas y una propuesta concreta de qué hacer con cada recomendación.

## Entradas

- La ficha con los hallazgos registrados.

## Pasos

1. Escribe «Conclusiones»: una respuesta por pregunta, citando los hallazgos (`#1`, `#3`).
2. Escribe «Recomendaciones»: qué haría falta, sin hacerlo, ordenado por severidad.
3. Convierte cada recomendación en una línea de «Promociones propuestas»: `- (tipo: adr | instruccion | mejora | documentacion) — destino — nota`. El destino es el paquete que la recogería (`decisiones-de-arquitectura`, `instrucciones-aprobadas`, `deuda-y-mejoras`, el paquete de documentación correspondiente).
4. Cierra: `python3 $P/scripts/comun/fichas.py estado AUD-… cerrada`.
5. Ejecuta las verificaciones: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-auditorias.py` (en `cerrada`, un `findings_count` distinto de la tabla es error).
6. **Detente.** Resume las conclusiones y pregunta a la persona qué promociones acepta.

## Criterio de salida

- Ficha `cerrada` con conclusiones, recomendaciones y promociones propuestas.
- Verificaciones sin errores y la persona con la decisión pendiente.
