# Caso: revisión semanal con una ADR olvidada y una instrucción nueva

## Pedido

«Usa el paquete revision-humana: ¿qué tengo pendiente de decidir?» Instalados: `instrucciones-aprobadas`, `decisiones-de-arquitectura` y este paquete; `dias_aviso: 14`.

## Recorrido

**recoger-pendientes.**

```
python3 $P/scripts/revision.py pendientes
ADR-20261012-usar-postgres	decisiones-de-arquitectura	propuesta	25 días	Usar PostgreSQL como base de datos
    persona: python3 uxyngraphar/paquetes/decisiones-de-arquitectura/scripts/comun/fichas.py estado ADR-20261012-usar-postgres <status> --humano  (status: aceptada, rechazada)
INS-20261106-filtro-pedidos	instrucciones-aprobadas	awaiting_approval	0 días	Filtrar pedidos por estado
    persona: python3 uxyngraphar/paquetes/instrucciones-aprobadas/scripts/comun/fichas.py estado INS-20261106-filtro-pedidos <status> --humano  (status: approved)
```

**priorizar-pendientes-antiguos** (skill):

```
python3 $P/scripts/verificar-revision.py
aviso: decisiones-de-arquitectura/ADR-20261012-usar-postgres lleva 25 días en «propuesta» esperando a una persona
revision-humana: 2 pendientes de decisión, 1 con más de 14 días
```

La ADR encabeza la revisión; salida propuesta: decidirla esta semana o rechazarla si ya no aplica.

**preparar-revision.**

```
python3 $P/scripts/revision.py preparar
```

`REVISION.md` queda así:

```
| Paquete | Ficha | Status | Días | Título | Opciones | Decisión |
|---|---|---|---|---|---|---|
| decisiones-de-arquitectura | ADR-20261012-usar-postgres | propuesta | 25 | Usar PostgreSQL como base de datos | aceptada, rechazada |  |
| instrucciones-aprobadas | INS-20261106-filtro-pedidos | awaiting_approval | 0 | Filtrar pedidos por estado | approved |  |
```

**detectar-status-desfasado** (skill): la ADR propone PostgreSQL; `docker-compose.yml` ya levanta `postgres:16` y `src/database/` usa el driver `pg`. Status desfasado: la decisión ya está aplicada y la ADR solo la regularizaría.

**resumir-pendiente** (skill), entregado en el chat:

- `ADR-20261012-usar-postgres` (25 días): fija PostgreSQL como base de datos del proyecto. Status desfasado: el código ya usa `pg` (`src/database/connection.ts`) y `docker-compose.yml` levanta `postgres:16`; aceptarla la hace vinculante, rechazarla deja ese uso sin decisión registrada. Ficha: `uxyngraphar/trabajo/decisiones-de-arquitectura/pendientes/ADR-20261012-usar-postgres.md`.
- `INS-20261106-filtro-pedidos` (hoy): aprobarla permite tocar 2 archivos de `src/orders/` para filtrar el listado por estado; la paginación queda fuera. Ficha: `uxyngraphar/trabajo/instrucciones-aprobadas/instrucciones/pendientes/INS-20261106-filtro-pedidos.md`.

Cómo decidir: escribir `aceptada`, `rechazada`, `approved` o `posponer` en «Decisión» y ejecutar `python3 $P/scripts/revision.py aplicar --humano`. El agente se detiene aquí.

**comprobar-decisiones.** La persona escribe `aceptada` y `approved`, ejecuta `aplicar` y comparte la salida:

```
ADR-20261012-usar-postgres → aceptada: hecho uxyngraphar/trabajo/decisiones-de-arquitectura/completadas/ADR-20261012-usar-postgres.md
INS-20261106-filtro-pedidos → approved: hecho uxyngraphar/trabajo/instrucciones-aprobadas/instrucciones/en-progreso/INS-20261106-filtro-pedidos.md
```

La instrucción se aprobó con `ciclo.py aprobar` (el comando que declara su paquete), no con `fichas.py estado`. `revision.py pendientes` responde `(nada espera una decisión)` y las verificaciones pasan.

## Resultado

- Las dos decisiones aplicadas por los comandos de sus paquetes, sin mover ninguna ficha a mano.
- La ADR antigua y desfasada salió a la luz y quedó regularizada.
