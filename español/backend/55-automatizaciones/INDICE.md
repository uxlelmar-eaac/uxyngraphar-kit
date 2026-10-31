# 55-automatizaciones — especificaciones
<!-- uxyngraphar:inicio -->

Las automatizaciones **no viven aquí**. Aquí vive su **especificación**:
qué valida cada una, contra qué sección de la documentación y con qué
criterios de aceptación. El agente las implementa en `automatizaciones/`
en la **raíz del proyecto** donde se adopte el pack.

## Contrato

1. El agente lee estas especificaciones y crea `<proyecto>/automatizaciones/`,
   un script o comando por especificación (nombres en minúsculas-con-guiones,
   iguales a los de aquí).
2. Cada implementación queda registrada en `35-herramientas/autorizadas/`
   del proyecto. Nada en `automatizaciones/` ejecuta sin estar catalogado.
3. Las especificaciones se leen en orden numérico; el número es estable.

## Catálogo

| # | Especificación | Fuente de verdad |
|---|----------------|------------------|
| 01 | [rutas-vivas](01-rutas-vivas.md) | `15-rutas/` |
| 02 | [anclas-rotas](02-anclas-rotas.md) | `15-rutas/`, `25-areas/*/CONTEXTO.md` |
| 03 | [espejo-completo](03-espejo-completo.md) | `50-sistema-integral/` |
| 04 | [decisiones-vinculantes](04-decisiones-vinculantes.md) | `00-nucleo/ciclo-vinculante.md`, `20-decisiones/` |
| 05 | [estados-con-fecha](05-estados-con-fecha.md) | `05-`, `20-`, `40-`, `45-`, `46-` + `validar-documentacion.py` |
| 06 | [herramientas-autorizadas](06-herramientas-autorizadas.md) | `35-herramientas/autorizadas/` |
| 07 | [humo-integral](07-humo-integral.md) | `50-sistema-integral/mapa-capas.md` |
| 08 | [manuales-vivos](08-manuales-vivos.md) | `30-manuales/` |
| 09 | [limite-lineas](09-limite-lineas.md) | protocolo del proyecto (defecto: 350) |
| 10 | [registro-vinculos](10-registro-vinculos.md) | `50-sistema-integral/` + código |

Protocolo: [_PROTOCOLO.md](_PROTOCOLO.md). Plantilla: [_PLANTILLA.md](_PLANTILLA.md).
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
