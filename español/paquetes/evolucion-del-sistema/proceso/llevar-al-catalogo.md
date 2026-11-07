---
fase: llevar-al-catalogo
resuelve: [propuestas-sin-llegar-al-catalogo]
skills: [preparar-exportacion]
---

# Fase: llevar al catálogo

Solo si la persona pide exportar EVO o revisar las aprobadas. Si no, esta fase no se recorre.

## Objetivo

Que las EVO aprobadas salgan hacia el catálogo por decisión de la persona y que su estado diga la verdad.

## Entradas

- Las EVO `approved` (y `pending`, si la persona quiere exportar también las pendientes).

## Pasos

1. Aplica `preparar-exportacion`: comprueba que cada EVO aprobada está completa y le das a la persona el comando.
2. La persona exporta: `python3 $P/scripts/evolucion.py exportar --humano [--todas]`. El script escribe `exportaciones/EXPORTACION-<fecha>.md` sin rutas absolutas y marca `exportada` en cada EVO.
3. Cuando el catálogo publica la versión que incorpora una EVO, recuerda a la persona que la pase a `done` (`--humano`) y que retire el ajuste local que la citaba en `adaptaciones-de-paquetes`, si existe.
4. Si una EVO `pending` ya está aplicada en el sistema, díselo a la persona: nunca queda `pending` algo aplicado.

## Criterio de salida

- Las EVO aprobadas están exportadas (o la persona decidió no hacerlo) y ninguna EVO tiene un estado falso.
