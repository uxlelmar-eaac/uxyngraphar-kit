# Ciclo integral de actos — guía operativa (cliente)

Complemento práctico de [ciclo-vinculante.md](../00-nucleo/ciclo-vinculante.md). **No repite reglas de PROTOCOLO**; ejemplos y matriz de lectura/escritura.

**Cliente:** BFF en `15-rutas/`; API externa por **`id`** en [registro-ids-compartidos.md](../00-nucleo/registro-ids-compartidos.md); espejo UI en `50-sistema-integral/`.

## Matriz acto × carpeta

| Carpeta | crear | editar | corregir | mejorar-docs | auditar | adoptar | revisar-pendientes |
|---------|-------|--------|----------|--------------|---------|---------|--------|
| `05-instrucciones/` (estados) | W | W | W | W | R | W | R |
| `25-areas/` | R/W | R/W | R/W | W | R | W | — |
| `15-rutas/` | R/W | R/W | R/W | W | R/W | W | — |
| `50-sistema-integral/` | W | W | W | W | W | W | — |
| `45-mejoras-propuestas/` (estados) | W cierre | W cierre | W cierre | — | — | — | R/W |
| `46-evolucion-documentacion/` (estados; solo sistema documental completo) | W cierre | W cierre | — | W cierre | — | W | R/W |
| `40-auditorias/` (estados) | — | — | R/W | — | W | — | R/W |
| `35-herramientas/` | W propuesta | — | — | — | — | R | R/W |

Leyenda: **R** leer si citado · **W** escribir en cierre/instrucción · **—** no por defecto

## Ejemplo 1 — Feature UI (`acto: crear`)

1. Crear instrucción desde [_PLANTILLA.md](../05-instrucciones/_PLANTILLA.md) con `vinculos_entrada: []` o issue/PR.
2. `lectura_minima`: CONTEXTO + ids API en registro (no ficha servidor duplicada).
3. Tras `approved`: codear anclas → sync operativa + `espejo_actualizar`.
4. Cierre: `vinculos_salida` = paths tocados; `mejoras_propuestas` si deuda detectada.

## Ejemplo 2 — Corrección bug (`acto: corregir`)

1. `vinculos_entrada`: id instrucción origen o ticket.
2. Mismo flujo que crear; alcance acotado al fix.
3. Si el bug revela refactor grande → **45**, no ampliar alcance.

## Ejemplo 3 — Gap del pack (`acto: adoptar` → EVO)

1. Durante adopción, marcar **F** en [matriz-cobertura-proyectos.md](../46-evolucion-documentacion/matriz-cobertura-proyectos.md).
2. Crear ficha `EVO-*` en `46-evolucion-documentacion/` (máx. 2 en instrucción).
3. Revisión de pendientes [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md) → aprobar → instrucción derivada con `vinculos_entrada: [EVO-...]`.
4. Al cerrar EVO: actualizar matriz.

## Ejemplo 4 — Cierre con 45 + 46

Instrucción `done` (movida a `05-instrucciones/03-completadas/YYYY-MM-DD/`) con vínculos por id:

```yaml
mejoras_propuestas:
  - MEJ-20260808-refactor-x
evolucion_documentacion:
  - EVO-20260808-guia-y
vinculos_salida:
  - docs/25-areas/auth/CONTEXTO.md
  - 45-mejoras-propuestas:MEJ-20260808-refactor-x
  - 46-evolucion-documentacion:EVO-20260808-guia-y
```

## Referencias

- [flujo-instrucciones-documentacion.md](flujo-instrucciones-documentacion.md)
- [estrategia-instrucciones.md](../00-nucleo/estrategia-instrucciones.md)
- [sync-documentacion-pr.md](sync-documentacion-pr.md)
