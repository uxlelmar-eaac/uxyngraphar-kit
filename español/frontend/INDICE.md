# Documentación — cliente
<!-- uxyngraphar:inicio -->

Índice maestro del pack frontend (**repo aislado**). En el repo: `docs/INDICE.md`; `AGENTES.md` en raíz.

## Empieza aquí (humano)

- **Guía visual:** [!00_franco-documentacion-practica.html](!00_franco-documentacion-practica.html) — flujo en 1 scroll
- **Tarjeta rápida:** [tarjeta-referencia-humana.md](10-guias/tarjeta-referencia-humana.md) — pedir → aprobar → revisión de pendientes

## Mapa carpeta → rol → cuándo leer

| Carpeta | Rol | Cuándo leer |
|---------|-----|-------------|
| [AGENTES.md](../AGENTES.md) (raíz repo) | Entrada obligatoria IA | Siempre primero |
| [ESTADO.md](ESTADO.md) | Última instrucción cerrada + pendientes (orientación) | Al entrar, si existe |
| [PROTOCOLO.md](PROTOCOLO.md) | Taxonomía y reglas; repo aislado | Crear/cambiar docs; dudas de flujo |
| [00-nucleo/](00-nucleo/INDICE.md) | Canon, config, registro ids, tokens | Instrucción o CONTEXTO lo citan |
| [05-instrucciones/](05-instrucciones/INDICE.md) | Contratos de tarea (estados + fechas) | Una instrucción `approved` por tarea (`02-en-progreso/`) |
| [10-guias/](10-guias/INDICE.md) | Onboarding, PR, adopción, estados | Instalación; no en tareas normales IA |
| [15-rutas/](15-rutas/INDICE.md) | Solo BFF propios | Citadas; API por **id** |
| [20-decisiones/](20-decisiones/INDICE.md) | ADR UI (estados + fechas) | Dominio afectado (`03-completadas/` = aceptadas) |
| [25-areas/](25-areas/INDICE.md) | CONTEXTO UI | Campo `areas` de instrucción |
| [30-manuales/](30-manuales/) | Ops / despliegue | Solo tareas operaciones |
| [35-herramientas/](35-herramientas/INDICE.md) | Herramientas UI autorizadas / propuestas (estados) | Excepción o revisión humana |
| [45-mejoras-propuestas/](45-mejoras-propuestas/INDICE.md) | Deuda/bugs IA (bandeja humana, estados) | Revisión humana de pendientes; IA solo escribe al cerrar |
| [46-evolucion-documentacion/](46-evolucion-documentacion/INDICE.md) | Meta-mejoras del sistema documental completo (estados) | Revisión de pendientes; revisión matriz; IA escribe al cerrar ≤2 |
| [40-auditorias/](40-auditorias/INDICE.md) | Investigaciones (estados) | Solo `02-en-progreso/` citadas |
| [50-sistema-integral/](50-sistema-integral/INDICE.md) | Espejo UI 1:1 scaffolding | Leer solo si `espejo_leer`; escribir al cerrar |
| [90-archivo/](90-archivo/INDICE.md) | Histórico | **Nunca** por defecto |
| [scripts/](scripts/validar-documentacion.py) | Validación opcional | Post-instalación / CI opcional |

## Organización por estados y fechas

Las secciones que acumulan documentos (`05`, `20`, `40`, `45`, `46`, `35/propuestas`) se organizan en `01-pendientes` … `06-listas-para-eliminar` y dentro, carpetas `YYYY-MM-DD` (R-17). El árbol es el índice; vista viva de pendientes: `python3 docs/scripts/decisiones/decisiones.py scan`. Detalle: [organizacion-estados-fechas.md](10-guias/organizacion-estados-fechas.md).

(En Windows: `py -3` en lugar de `python3`.)

## Flujo rápido IA

0. ¿Herramienta autorizada? → ficha + anclas.
1. Instrucción `approved` (`05-instrucciones/02-en-progreso/YYYY-MM-DD/`) → `lectura_minima` → CONTEXTO → ids API (registro) → anclas UI.
2. Cierre: operativa + `espejo_actualizar` + mover a `03-completadas/` (R-17).

Detalle: [eficiencia-ia.md](00-nucleo/eficiencia-ia.md) · [estrategia-instrucciones.md](00-nucleo/estrategia-instrucciones.md).

## Primera adopción

[10-guias/instalacion-docs.md](10-guias/instalacion-docs.md) · [10-guias/adopcion-pack.md](10-guias/adopcion-pack.md) · [_PLANTILLA-adopcion-inicial-pack.md](05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md).

## API en otro repo

[00-nucleo/registro-ids-compartidos.md](00-nucleo/registro-ids-compartidos.md) · [10-guias/sync-multi-repo.md](10-guias/sync-multi-repo.md).
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
