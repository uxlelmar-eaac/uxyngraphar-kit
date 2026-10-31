# AGENTES.md — entrada obligatoria para IA

**Lee solo este archivo al empezar** una tarea sobre el kit uxyngraphar (instalar, configurar, explicar o documentar el uso). Luego abre **únicamente** los enlaces que este playbook indique para el paso en curso.

- Este archivo gobierna el **manual del kit** (`documentacion/`).
- Si el trabajo es **dentro de un proyecto ya sembrado**, lee el `AGENTES.md` **de ese proyecto** (junto a su `docs/`), no reescribas el núcleo del pack.

No edites `español/backend|frontend|_compartido` salvo instrucción humana explícita. Sí puedes actualizar `documentacion/` si te lo piden.

## Objetivo

Dejar un proyecto **con el pack sembrado, configurado y usable**, e **instruir a la persona** con claridad.

## Playbook (orden fijo)

1. **Requisitos** → [01-instalacion/requisitos.md](01-instalacion/requisitos.md)  
   Windows: preferir `py -3` si no hay `python3`.
2. **Herramienta** (si falta) → [01-instalacion/herramienta.md](01-instalacion/herramienta.md)  
   Verifica `uxyngraphar version`. Si falla: PATH / terminal nueva / `UXYNGRAPHAR_HOME`.
3. **Confirmar con el humano** (obligatorio antes de escribir):
   - Ruta(s) del repo
   - Pack: `servidor` | `cliente` | `ambos`
   - Layout: un repo / monorepo (subs) / dos repos
   - Colaborar EVO: por defecto al automatizar **`--colaborar no`**  
     Recuerda: `--si` sin `--colaborar` = No; si lo ejecutas tú (agente), la pregunta queda pendiente para la persona.
4. **Sembrar** → [01-instalacion/sembrar-proyecto.md](01-instalacion/sembrar-proyecto.md)  
   - Un pack en raíz: `--pack servidor|cliente --si --colaborar no`
   - Monorepo ambos: **`--mismo-repo`** + `--sub-servidor` / `--sub-cliente` (no inventes `apps/api` si el layout es otro) → [06-packs/monorepo.md](06-packs/monorepo.md)
   - Dos repos: `--proyecto` + `--proyecto2` **sin** `--mismo-repo`
   - Flags completos: [05-comandos/referencia-cli.md](05-comandos/referencia-cli.md) — **no inventes flags**
5. **Configurar** → [04-uso-ia/instalar-y-configurar.md](04-uso-ia/instalar-y-configurar.md) y [02-configuracion/](02-configuracion/configuracion-proyecto.md)  
   No edites `uxyngraphar.config.json` sin confirmación humana. **No** ejecutes `feedback.py activar|enviar`.
6. **Verificar** → [02-configuracion/doctor.md](02-configuracion/doctor.md)  
   `python3 docs/scripts/doctor.py` (ruta según subcarpeta). Remedia con `--fix` solo si el propio doctor lo indica como seguro.
7. **Cerrar** → checklist [01-instalacion/checklist.md](01-instalacion/checklist.md) + [04-uso-ia/instruir-humano.md](04-uso-ia/instruir-humano.md)

## Reglas duras

- No actives ni envíes sugerencias EVO.
- No edites el **núcleo** instalado a mano (`10-guias/`, `scripts/`, `PROTOCOLO.md`, lock…).
- No inventes carpetas numeradas del pack (R-14).
- No leas `95-memoria/` (R-24).
- Límites: [04-uso-ia/limites.md](04-uso-ia/limites.md).
- Salto **MAYOR** de versión: no fuerces `actualizar`; sigue `actualizar-pack.py --migracion-aprobada` ([03-uso-humano/actualizar.md](03-uso-humano/actualizar.md)).

## Si te piden “solo explicar”

Usa [00-inicio/que-es.md](00-inicio/que-es.md), [05-comandos/referencia-cli.md](05-comandos/referencia-cli.md) y [INDICE.md](INDICE.md). No ejecutes instaladores sin pedido explícito.
