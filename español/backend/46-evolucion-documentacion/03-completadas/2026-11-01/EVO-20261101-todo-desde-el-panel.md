---
id: EVO-20261101-todo-desde-el-panel
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - AGENTES.md
  - 10-guias/respaldos.md
  - 10-guias/memoria.md
  - 10-guias/envio-sugerencias.md
  - 10-guias/configuracion-uxyngraphar.md
  - 10-guias/tarjeta-referencia-humana.md
proposed_at: 2026-11-01
instruction_derivada: solicitud-humana-20261101-todo-desde-el-panel
---
# EVO-20261101 — Todo desde el panel: un solo comando

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita (uxlelmar, 2026-11-01): «dejar de usar la consola de comandos y que todo se pueda gestionar, configurar, actualizar de forma sencilla, directa y rápida desde el panel visual. Que como tal el único comando que se utilice con la consola de comandos es para abrir el panel.»

## Qué faltaba

El panel (`uxyngraphar panel`) ya configuraba proyectos, la plantilla y la versión, pero el día a día de una persona seguía en la terminal: aprobar instrucciones, el doctor y sus arreglos, restaurar copias, buscar en la memoria, ganchos, CODEOWNERS, cambiar de versión, el PATH o desinstalar. Las guías del pack le decían a la persona «ejecuta `python3 uxyngraphar/scripts/…`».

## Inventario (qué se le pide hoy a una persona y dónde queda)

| Comando o script | Antes | Ahora |
|---|---|---|
| `uxyngraphar` (sin argumentos) | imprimía la ayuda | abre el panel (sin persona delante, CI o agente: sigue imprimiendo la ayuda) |
| `uxyngraphar panel` | panel | igual (es el mismo comando) |
| `uxyngraphar instalar` | panel (asistente) | igual |
| `uxyngraphar actualizar [--todos]` | panel, uno a uno | panel: uno o «Actualizar todos» |
| `uxyngraphar estado` / `proyectos [--agregar/--quitar/--salud]` / `configuracion` / `mover-carpeta` | panel | igual |
| `uxyngraphar autoactualizar` | panel (había que reabrirlo) | panel, y se reinicia solo en la versión nueva |
| `uxyngraphar usar X.Y.Z` / `version` | solo terminal | panel → Sistema |
| PATH del comando | solo en la bienvenida | panel → Sistema (añadir o quitar cuando quieras) |
| `uxyngraphar desinstalar` | solo terminal | panel → Sistema (confirmación escrita) |
| Proyectos registrados que ya no existen / candado de instalación abandonado | a mano | panel → Sistema → Limpiar |
| `doctor.py` / `doctor.py --fix` | terminal | panel → Proyecto → Salud (Arreglar, con copia antes) |
| `decisiones.py scan/register/apply` (aprobar instrucciones, MEJ, EVO, propuestas, ADR) | terminal o editar el frontmatter | panel → Proyecto → Pendientes (leer, ver el cambio, confirmar; con copia) |
| `respaldos.py listar/ver/restaurar/limpiar` | terminal | panel → Proyecto → Copias de seguridad |
| `memoria.py buscar/ver/recuperar/purgar` | terminal | panel → Proyecto → Memoria |
| `feedback.py estado/previsualizar/activar/revocar/enviar` | terminal (activar/revocar ya en el panel) | panel → Proyecto → Configuración → Colaborar |
| `instalar-ganchos.py [--pre-push/--quitar]` | terminal | panel → Proyecto → Protecciones |
| CODEOWNERS (`--propietario`) | solo al instalar | panel → Proyecto → Protecciones |
| `reglas.py listar/validar` | terminal | panel → Proyecto → Reglas y fichas |
| `decisiones.py archivar/limpiar` | terminal | panel → Proyecto → Reglas y fichas (vista previa y mover) |
| `verificar-nucleo.py`, `validar-documentacion.py` | terminal | dentro de Salud (el doctor los incluye); siguen para CI y ganchos |
| `controlar.py`, `verificar-espejo.py`, `escanear-secretos.py`, `contexto.py`, `presupuesto.py`, `costo-tokens.py`, `espejo-mapa.py`, `exportar-evo.py`, `decisiones.py new/cerrar/estado/metricas`, `reglas.py indice`, `ajustes.py` | terminal | se quedan: los usan los agentes, el CI y los ganchos, no la persona |
| `actualizar-pack.py --migracion-aprobada` (salto mayor) y `decisiones.py depurar` (plan JSON) | terminal | se quedan por ahora: piden una instrucción aprobada y los prepara el agente |
| Instalador de una línea (`curl … \| python3 -`) | terminal | se queda: es lo que instala la herramienta (una vez por equipo) |

## Decisión

- El panel hace todo lo de la tabla con el mismo patrón que ya tenía: solo en 127.0.0.1 con token, lo que escribe exige una persona delante (nunca CI ni un agente), vista previa antes de cambiar nada y copia en `.uxyngraphar-respaldo/` cuando toca archivos (se restaura desde el propio panel). Cada acción usa los scripts de la versión del pack que tiene el proyecto.
- `uxyngraphar` sin argumentos abre el panel; `uxyngraphar ayuda` sigue mostrando los comandos. Todos los comandos siguen funcionando igual (CI, agentes y scripts dependen de ellos): se presentan como avanzados.
- Las guías del pack y `AGENTES.md` dicen a la persona dónde está cada cosa en el panel; las órdenes de terminal quedan como alternativa avanzada. Sin cambios en el texto de las reglas R-xx.
