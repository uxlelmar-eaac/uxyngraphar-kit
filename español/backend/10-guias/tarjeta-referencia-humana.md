# Tarjeta de referencia humana — servidor

Una página: **qué hacer tú** y **qué hace la IA**. Guía visual: [!00_banco-documentacion-practica.html](../!00_banco-documentacion-practica.html).

**¿Qué es “revisión de pendientes”?** Revisar periódicamente las **bandejas** donde la IA dejó cosas sin ejecutar: instrucciones por aprobar, mejoras (45), cambios al pack (46) y propuestas de herramientas. Se hace con [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md) (aprobar / posponer / rechazar).

## Tres momentos

| Momento | Tú | IA |
|---------|-----|-----|
| **1 — Pedir** | Describe el cambio en lenguaje natural | Redacta instrucción `awaiting_approval` + plan |
| **2 — Aprobar** | Revisa alcance; marca `decision:aprobar` | Espera `approved`; no codea |
| **3 — Revisión de pendientes** | [`decisiones-pendientes`](../35-herramientas/autorizadas/decisiones-pendientes.md) periódico | Ya cerró con `done` + colas 45/46 si aplica |

## Cuándo instrucción vs revisión de pendientes vs herramienta

| Situación | Acción |
|-----------|--------|
| Feature, fix, endpoint nuevo | Instrucción normal ([`_PLANTILLA.md`](../05-instrucciones/_PLANTILLA.md)) |
| Solo actualizar docs / espejo | [`_PLANTILLA-solo-documentacion.md`](../05-instrucciones/_PLANTILLA-solo-documentacion.md) |
| Acción repetible ya autorizada | Pedir en chat → IA ejecuta ficha autorizada **sin** instrucción nueva |
| Revisar bandejas MEJ / EVO / propuestas | `python3 docs/scripts/decisiones/decisiones.py scan` |
| Cambio al pack (taxonomía, plantillas) | Aprobar `EVO-*` → instrucción derivada; **no** pedir a la IA que reorganice carpetas |

(En Windows: `py -3` en lugar de `python3`.)

## Redactar `lectura_minima`

Máx. ~3 paths operativos; nunca índices ni guías. Ver [redaccion-lectura-minima.md](redaccion-lectura-minima.md).

## Checklist verificación de linaje (por PR)

Para cada cambio, confirmar:

- [ ] ¿Qué instrucción `id` gobierna este PR?
- [ ] ¿`vinculos_entrada` documentan el origen (issue, EVO, MEJ, instrucción previa)?
- [ ] ¿`vinculos_salida` listan paths docs tocados al cerrar?
- [ ] ¿MEJ/EVO nuevos tienen ficha y están en frontmatter de la instrucción?
- [ ] ¿Decisión humana registrada (checkbox o `decisiones-pendientes`)?
- [ ] ¿Cada nombre nuevo elimina la necesidad de un comentario? Rechaza `data`, `tmp`, `mgr` y constantes mágicas ([R-23](../00-nucleo/nombres-autoexplicativos.md))

## Revisión trimestral

- [ ] Pendientes 46 + [matriz cobertura](../46-evolucion-documentacion/matriz-cobertura-proyectos.md)
- [ ] Todo `EVO-*` / `MEJ-*` `approved` tiene `instruction_derivada` o está en `05-canceladas/`
- [ ] Instrucciones `done` antiguas → `05-instrucciones/04-archivadas/`
- [ ] CI estricto: [ci-validacion-documentacion.md](ci-validacion-documentacion.md)

## Referencias

- [flujo-instrucciones-documentacion.md](flujo-instrucciones-documentacion.md)
- [mejoras-propuestas-ia.md](mejoras-propuestas-ia.md)
