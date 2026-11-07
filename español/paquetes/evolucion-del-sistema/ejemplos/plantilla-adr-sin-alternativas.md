# Caso: la plantilla de ADR no tiene sitio para las alternativas descartadas

## Pedido

La persona pide registrar una decisión con `decisiones-de-arquitectura`: «elegimos PostgreSQL frente a MongoDB y DynamoDB; deja claro por qué descartamos las otras dos». La plantilla `plantillas/adr.md` de ese paquete solo tiene «Contexto», «Opciones», «Decisión» y «Consecuencias»: no hay dónde explicar por qué se descarta cada opción. `evolucion-del-sistema` está instalado.

## Recorrido

**detectar-carencia.** El hueco es del sistema (una plantilla de un paquete), no del producto. Tentación: añadir la sección a `uxyngraphar/paquetes/decisiones-de-arquitectura/plantillas/adr.md`. No se hace: `verificar-integridad.py` lo marcaría como alterado y la siguiente actualización lo borraría. La ADR de hoy se redacta con las alternativas dentro de «Opciones», y la carencia se anota.

**registrar-evo.** Sin duplicados:

```
python3 $P/scripts/comun/fichas.py listar evo --status pending
```

No devuelve nada. Con `redactar-evo`:

```
python3 $P/scripts/comun/fichas.py nueva evo --slug adr-sin-alternativas --titulo "La plantilla de ADR no recoge alternativas descartadas"
…/trabajo/evolucion-del-sistema/pendientes/EVO-20261106-adr-sin-alternativas.md
```

Antes de rellenarla, la verificación avisa:

```
python3 $P/scripts/verificar-evolucion.py
aviso: EVO-20261106-adr-sin-alternativas: sección «evidencia» sin rellenar
aviso: EVO-20261106-adr-sin-alternativas: sección «propuesta» sin rellenar
evolucion-del-sistema: 0 errores, 2 avisos
```

Se rellena: `tipo: plantilla`, `paquete: decisiones-de-arquitectura`, `prioridad: pronto`, `detectada_en: ADR-20261106-base-de-datos`. Evidencia: «al redactar `ADR-20261106-base-de-datos`, los motivos de descarte de MongoDB y DynamoDB quedaron mezclados con la descripción de las opciones». Propuesta: «`plantillas/adr.md`: añadir “## Alternativas descartadas” (una línea por opción con el motivo) entre “Opciones” y “Decisión”». `verificar-evolucion.py` queda en `0 errores, 0 avisos`.

Al cerrar, el agente dice: «Registré la ADR. Además, `EVO-20261106-adr-sin-alternativas` propone añadir “Alternativas descartadas” a la plantilla de ADR; no he tocado el paquete.»

**llevar-al-catalogo.** El agente no puede aprobar ni exportar:

```
python3 $P/scripts/comun/fichas.py estado EVO-20261106-adr-sin-alternativas approved
error: «approved» solo lo asigna una persona (usa --humano si eres tú)
python3 $P/scripts/evolucion.py exportar
error: exportar es una acción de la persona (--humano)
```

La persona la aprueba con `--humano` y, a petición suya, el agente aplica `preparar-exportacion`: la EVO no contiene datos internos y le da el comando `evolucion.py exportar --humano`. La persona lo ejecuta, el informe queda en `exportaciones/EXPORTACION-2026-11-06.md` y la EVO con `exportada: 2026-11-06`. Cuando el catálogo publique la versión de `decisiones-de-arquitectura` con la sección nueva, la persona la pasará a `done`.

## Resultado

- La ADR del día registrada sin editar ningún paquete.
- `EVO-20261106-adr-sin-alternativas` aprobada y exportada; ningún archivo de `uxyngraphar/paquetes/` alterado.
