---
name: redactar-evo
description: Crea una ficha EVO con fichas.py y la rellena con tipo, paquete afectado, prioridad, qué falta en el sistema, evidencia y propuesta concreta sobre archivos del paquete.
resuelve: [carencias-del-sistema-sin-registro, paquetes-editados-en-el-proyecto]
---

# Redactar EVO

## Cuándo usarla

- En la fase `registrar-evo`, cuando no hay una EVO previa de la misma carencia.

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva evo --slug <slug> --titulo "…"`. Nace `pending` en `uxyngraphar/trabajo/evolucion-del-sistema/pendientes/`.
2. Frontmatter: `tipo` de `ajustes.tipos` (`cobertura`, `proceso`, `plantilla`, `paquete-nuevo`, `herramienta`), `paquete` (id del paquete afectado, o `null` si es del sistema en general), `prioridad` (`ahora`, `pronto`, `despues`) y `detectada_en` (la instrucción o tarea).
3. «Qué falta en el sistema»: qué paquete, plantilla o proceso no cubre el caso. Del sistema, no del producto.
4. «Evidencia»: dónde se notó (tarea, `ruta:línea` del paquete o del proyecto, pasos).
5. «Propuesta»: qué archivo del paquete cambiaría y en qué sentido (`plantillas/adr.md`: añadir «Alternativas descartadas»), sin aplicarlo.
6. Deja «Decisión a tomar» como está: es para la persona.

## Resultado

- EVO `pending` que `verificar-evolucion.py` acepta sin avisos (tipo válido, evidencia y propuesta rellenas, paquete instalado).
