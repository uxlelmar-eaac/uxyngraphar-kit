---
fase: implementar
resuelve: [capas-mal-importadas, modulos-acoplados, comun-dependiente-del-negocio]
skills: [corregir-dependencia-de-capa]
---

# Fase: implementar

## Objetivo

Hacer el cambio pedido colocando cada pieza en la capa que le corresponde, sin añadir imports que el perfil no permite.

## Entradas

- Módulo y capas identificados en `diagnosticar` (y el módulo creado en `disenar-modulo`, si aplica).
- `COMPONENTES.md`: qué puede importar cada capa.

## Pasos

1. Antes de escribir un import entre carpetas, comprueba en `COMPONENTES.md` que la capa de origen puede importar la de destino.
2. Si necesitas algo de otro módulo, añade o usa un método en `integrations/`; nunca importes su `application/` ni su `infrastructure/`.
3. Si algo es útil para varios módulos y no tiene negocio, va a lo común; si tiene negocio, se queda en su módulo.
4. Si una dependencia no encaja, aplica la skill `corregir-dependencia-de-capa`.
5. Si la única salida rompe un límite, detente: pasa a `registrar-desviacion`.

## Criterio de salida

- El cambio está hecho y ningún import nuevo rompe el perfil.
