# Memoria del sistema (`95-memoria/`)

Única guía sobre la memoria (regla **R-24**): dónde terminan las fichas en lugar de borrarse, cómo las consulta una persona y cómo se mantiene fuera del alcance del agente.

## Qué es

Las colas por estado (R-17) crecen sin parar: instrucciones hechas, decisiones reemplazadas, auditorías cerradas. En uxyngraphar **nada se borra**: lo que sale de `06-listas-para-eliminar` (o lleva mucho tiempo archivado) pasa a `docs/95-memoria/`, tal cual, con el motivo y la fecha. El contexto del agente queda limpio y la historia del proyecto sigue a mano para quien la necesite.

| Pregunta | Respuesta |
|----------|-----------|
| ¿Quién la lee? | Solo una persona, con `memoria.py`. El agente nunca. |
| ¿Se edita? | No. Solo se añade. Una memoria tocada a mano bloquea el commit. |
| ¿Se puede sacar algo? | Sí: `recuperar` la devuelve a `04-archivadas`; `purgar` la borra de verdad (solo datos sensibles). |
| ¿Pesa en git? | Lo mismo que antes: son las mismas fichas, en otra carpeta. |

## Qué entra y cuándo

`decisiones.py depurar` propone pasar a la memoria (nunca lo hace solo):

| Ficha en | Tras | Clave de configuración |
|----------|------|------------------------|
| `06-listas-para-eliminar` | 30 días | `memoria.listas_a_memoria_dias` |
| `04-archivadas` | 180 días | `memoria.archivadas_a_memoria_dias` |

La antigüedad se mide por la carpeta de fecha (R-17). Además, una persona puede guardar a mano cualquier ficha de `03`, `04`, `05` o `06` con `memoria.py guardar`. Las fichas vivas (`01`, `02`) no se guardan.

**Enlaces:** una ficha que todavía enlaza un documento vivo no se guarda (se explica cuál). Quita el enlace o cámbialo por el texto `memoria:ID`, que no es un enlace y el agente no sigue.

```bash
python3 docs/scripts/decisiones/decisiones.py depurar --plan plan.json         # informe + plan editable
# en plan.json: "aprobado": true y "motivo" en cada ítem con "accion": "memoria"
python3 docs/scripts/decisiones/decisiones.py depurar --aplicar plan.json      # simula
python3 docs/scripts/decisiones/decisiones.py depurar --aplicar plan.json --apply
```

(En Windows: `py -3` en lugar de `python3`.)

## Cómo está guardada

```text
docs/95-memoria/
├── INDICE.md                  explicación para personas
├── catalogo.jsonl             un apunte por hecho: guardada · recuperada · purgada (solo se añade)
├── registro-accesos.jsonl     quién buscó, vio, recuperó o purgó qué y cuándo
└── <sección>/<AAAA>/<AAAA-MM>/<ficha>.md
```

- Secciones: `instrucciones`, `decisiones`, `auditorias`, `mejoras`, `evolucion`, `herramientas`. Las carpetas son por la fecha en que se guardó.
- La ficha conserva su frontmatter y gana `memoria_desde` (ruta original), `memoria_estado_previo`, `memoria_guardada` y `memoria_motivo`.
- Cada apunte `guardada` del catálogo lleva la huella sha256 de la ficha: así se sabe si alguien la tocó.

## Consultar (solo personas)

```bash
python3 docs/scripts/memoria.py buscar pagos                      # busca en el catálogo: id, título, motivo, ruta original
python3 docs/scripts/memoria.py buscar --seccion decisiones       # todo lo de una sección
python3 docs/scripts/memoria.py ver INS-20260110-cobros           # muestra la ficha en la terminal
python3 docs/scripts/memoria.py guardar 05-instrucciones/03-completadas/2026-01-10/tarea.md --motivo "ya no aplica"
python3 docs/scripts/memoria.py recuperar INS-20260110-cobros     # vuelve a 05-instrucciones/04-archivadas/2026-01-10/
python3 docs/scripts/memoria.py verificar                         # integridad (cualquiera puede ejecutarlo)
```

En un monorepo añade `--docs apps/api/docs` antes del subcomando. Todo salvo `verificar` exige una persona en la terminal (o `UXYNGRAPHAR_HUMANO=1`) y queda en `registro-accesos.jsonl`. Tras `guardar`, `recuperar` o `purgar`, haz commit como con cualquier otro cambio.

**Recuperar** devuelve la ficha a `04-archivadas` (con `status: archivada`, u `obsoleta` en decisiones), sin el bloque `memoria_*`. Desde ahí vuelve a ser visible para el agente.

## Si una tarea del agente necesita algo de la memoria

El agente no la busca ni la pide por ruta. Si una instrucción la necesita:

1. La persona busca con `memoria.py buscar` y decide qué hace falta.
2. O bien la **recupera** (vuelve a ser una ficha archivada, visible), o bien copia el fragmento necesario en la instrucción, citando `memoria:ID`.

(Un préstamo temporal y controlado al agente llegará en una versión posterior.)

## Cómo se mantiene fuera del alcance del agente

| Barrera | Qué hace |
|---------|----------|
| `AGENTES.md` y R-24 | El agente sabe que no debe leerla, buscarla ni ejecutar nada en ella. |
| Reglas `deny` en `.claude/settings.json` | Claude Code no puede leer, editar ni escribir `docs/95-memoria/**`. |
| `.cursorignore`, `.geminiignore`, `.aiexclude` | Cursor, Gemini y otras herramientas la dejan fuera de su índice. |
| Herramientas del pack | Validador, `contexto.py`, `paquete.py`, métricas, espejo y decisiones la ignoran; `paquete.py` rechaza una ruta de la memoria. |
| `controlar.py` (control `memoria`, bloqueante) y CI | Cualquier cambio en la carpeta que no venga de `memoria.py` (una ficha tocada, borrada o añadida a mano) bloquea el commit y el PR. |
| `CODEOWNERS` | Los cambios en la memoria piden revisión del responsable. |

`doctor.py` comprueba que todo esté en su sitio y `doctor.py --fix` repone los archivos de exclusión y las reglas `deny`.

**Límite honesto:** estas barreras cubren a los agentes que respetan sus archivos de configuración y a cualquier cambio que llegue a un commit. Un agente con terminal libre podría abrir un archivo a mano; por eso la regla, la revisión humana y la integridad (nadie puede cambiar la memoria sin que se note) van juntas. Si una ficha contiene un secreto, no basta con la memoria: púrgala.

## Purgar (borrado definitivo)

Solo para un dato que no debe existir (una clave, datos personales):

```bash
python3 docs/scripts/memoria.py purgar INS-20260110-cobros --confirmar INS-20260110-cobros --motivo "contenía un token"
```

- El catálogo guarda que se purgó, cuándo, quién y por qué; **nunca** el contenido.
- La ficha sigue en el historial de git. Para un secreto, **rota la credencial** y, si hace falta, limpia el historial (`git filter-repo`) con tu equipo.
- `"memoria": {"permitir_purgar": false}` en `uxyngraphar.config.json` desactiva `purgar` en el proyecto.

## Configuración

```json
"memoria": {"archivadas_a_memoria_dias": 180, "listas_a_memoria_dias": 30, "permitir_purgar": true}
```

Detalle de cada clave: [configuracion-uxyngraphar.md](configuracion-uxyngraphar.md). Estados y fechas: [organizacion-estados-fechas.md](organizacion-estados-fechas.md).
