# uxyngraphar — pack documental servidor (backend/API)
<!-- uxyngraphar:inicio -->

**uxyngraphar** (contrato escrito firmado y sellado por todas las partes) es el nombre de este sistema documental: el **contrato** que ata a la IA y el **espejo** que la mantiene fiel al código.

Pack **autosuficiente** de documentación gobernada para colaboración humano–IA en un repositorio backend: instrucciones como contrato, presupuesto de tokens, ciclo vinculante de actos, espejo 1:1 del código, colas 45/46 y revisión de pendientes por CLI. Todo lo que el pack necesita para trabajar está **dentro de esta carpeta**; se copia a proyectos distintos y vive de forma independiente.

**Versión:** `1.0.0` — fuente única: [VERSION.md](VERSION.md) · historial: [CHANGELOG.md](CHANGELOG.md).

## Empieza aquí

| Quién | Entrada |
|-------|---------|
| Humano | [INDICE.md](INDICE.md) · [tarjeta rápida](10-guias/tarjeta-referencia-humana.md) · [guía visual](!00_banco-documentacion-practica.html) |
| Agente IA | [AGENTES.md](../AGENTES.md) (único doc de entrada; alias [AGENTS.md](../AGENTS.md)) · resumen en [REGLAS.md](REGLAS.md) · orientación entre sesiones: [ESTADO.md](ESTADO.md) |

## Instalación en un repo

- **Asistente (recomendado):** desde un clon de uxyngraphar, `python3 español/instalar.py` en cualquier sistema. Muestra el plan exacto antes de escribir.
- **Terminal:** `python3 scripts/instalar-pack.py . --repo RUTA/AL/REPO --proteger` (desde esta carpeta). Copia el núcleo a `docs/`, `AGENTES.md` a la raíz, escribe `docs/.uxyngraphar.lock` y valida.
- **Actualizar** un proyecto que ya lo tiene: `python3 español/actualizar.py RUTA_PROYECTO` o `python3 docs/scripts/actualizar-pack.py RUTA/AL/PACK` (simula; añade `--apply` para aplicar). Tu contenido no se toca.

(En Windows: `py -3` en lugar de `python3`.)

Detalle y pasos manuales de referencia: [10-guias/instalacion-docs.md](10-guias/instalacion-docs.md). Después, rellena [00-nucleo/configuracion-proyecto.md](00-nucleo/configuracion-proyecto.md).

Primera adopción guiada: [05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md](05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md) · Roadmap y **perfil mínimo**: [10-guias/adopcion-pack.md](10-guias/adopcion-pack.md). Organización de secciones que crecen: [10-guias/organizacion-estados-fechas.md](10-guias/organizacion-estados-fechas.md) (R-17).

## Relación con el pack cliente

Este pack es la **fuente de verdad del API**: las fichas HTTP viven en `15-rutas/` y el cliente las cita por `id` vía [00-nucleo/registro-ids-compartidos.md](00-nucleo/registro-ids-compartidos.md). Existe un pack hermano `cliente/` (frontend/UI) con la misma metodología.

## Gobernanza del pack

| Archivo | Rol |
|---------|-----|
| [CHANGELOG.md](CHANGELOG.md) | Evolución versionada (viaja con el pack) |
| `PARIDAD-PACKS.md` | Qué archivos comparte con el pack hermano (solo en el repo fuente de uxyngraphar; no se instala en proyectos) |
| [scripts/verificar-paridad.py](scripts/verificar-paridad.py) | Verifica los `identico` cuando ambos packs están juntos; en un repo aislado se desactiva solo |
| [scripts/instalar-pack.py](scripts/instalar-pack.py) · [actualizar-pack.py](scripts/actualizar-pack.py) · [verificar-nucleo.py](scripts/verificar-nucleo.py) · [doctor.py](scripts/doctor.py) · [contexto.py](scripts/contexto.py) · [presupuesto.py](scripts/presupuesto.py) · [exportar-evo.py](scripts/exportar-evo.py) · [respaldos.py](scripts/respaldos.py) · [costo-tokens.py](scripts/costo-tokens.py) | Instalar, actualizar (tres vías) y verificar la integridad del núcleo — ver [instalacion-docs.md](10-guias/instalacion-docs.md) y [actualizar-nucleo.md](10-guias/actualizar-nucleo.md) |
| [scripts/validar-documentacion.py](scripts/validar-documentacion.py) | Validación del pack (CI opcional: [10-guias/ci-validacion-documentacion.md](10-guias/ci-validacion-documentacion.md)) |

La estructura del pack es intencional e **intocable por IA** sin aprobación humana (regla R-14 de [PROTOCOLO.md](PROTOCOLO.md)); su evolución se propone vía fichas `EVO-*` en `46-evolucion-documentacion/`.
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
