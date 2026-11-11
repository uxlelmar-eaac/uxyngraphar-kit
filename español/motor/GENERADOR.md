# Generador de sistemas

`motor/generador.py` crea sistemas del catálogo siguiendo el protocolo de `sistemas-de-gobernanza/_base/`, para personas y para agentes de IA.
No sustituye a las normas: el contrato es [`ESPECIFICACION.md`](ESPECIFICACION.md), los nombres [`NOMENCLATURA.md`](NOMENCLATURA.md)
y el criterio de diseño [`GUIA-DE-SISTEMAS.md`](GUIA-DE-SISTEMAS.md). Los agentes siguen además
[`GUIA-PARA-AGENTES.md`](GUIA-PARA-AGENTES.md).

## Dos modos

| Modo | Cuándo | Cómo |
|------|--------|------|
| Completo | El sistema ya está pensado (alcance, fases, skills) | `generar plantilla` → editar la especificación → `generar desde` (simula) → `generar desde --aplicar` |
| Guiado | Se va pensando sobre la marcha | `crear` (esqueleto con marcadores `{{…}}`) → `generar pendientes` → rellenar → repetir hasta «listo» |

En el panel: Catálogo → Modo avanzado → «Crear sistema», pestaña «Esqueleto» o «Desde especificación». El editor de cada
sistema muestra sus pendientes y la siguiente acción.

## Comandos

```bash
uxyngraphar generar plantilla --id contratos-de-pago --familia proceso > spec.json   # especificación de partida
uxyngraphar generar desde spec.json                  # simula: errores, avisos y archivos que crearía
uxyngraphar generar desde spec.json --aplicar        # lo crea en sistemas-de-gobernanza/ solo si valida sin errores
uxyngraphar generar desde - --aplicar --json < spec.json   # desde la entrada estándar, salida JSON
uxyngraphar generar pendientes contratos-de-pago [--json]  # qué falta (archivo:línea) y la siguiente acción
uxyngraphar validar contratos-de-pago --json         # errores y avisos en JSON
uxyngraphar crear contratos-de-pago --titulo "Contratos de pago" --familia proceso --json   # esqueleto + pendientes
```

Códigos de salida: `0` sin errores (en `pendientes`, sistema listo); `1` con errores o pendientes.

### Garantías

- **Nada a medias:** `generar desde` construye el sistema en una carpeta oculta del catálogo (`sistemas-de-gobernanza/.generando-*`),
  lo valida igual que `validar` (estructura, piezas, nomenclatura y choques con el resto del catálogo) y solo entonces lo
  mueve a `sistemas-de-gobernanza/<id>/`. Si algo falla, el catálogo queda como estaba.
- **Sin marcadores:** una especificación con `{{…}}` en cualquier texto se rechaza.
- **Misma base:** usa `catalogo.crear` y las semillas de `_base/piezas/`; `scripts/comun/` sale idéntico a `_base`.

## Especificación (formato 1)

JSON. `generar plantilla` da una completa y válida en forma, con una clave `_ayuda` que el generador ignora.

| Campo | Obligatorio | Se convierte en |
|-------|-------------|-----------------|
| `formato` | no (1) | — |
| `id`, `titulo`, `descripcion`, `familia` | sí | `sistema.json` (NOMENCLATURA.md §1–2) |
| `activacion` | no | frases extra; el id y el id con espacios se añaden solos |
| `resumen`, `que_resuelve` | sí | apertura y «Qué resuelve» de `SISTEMA.md` |
| `problemas` `[{id, descripcion}]` | sí, ≥1 | `alcance.problemas` y «Problemas que cubre» |
| `fuera_de_alcance` `[{tema, derivar_a}]` | sí, ≥1 | `alcance.fuera_de_alcance` y «Fuera de alcance»; `derivar_a` es un sistema del catálogo o `null` |
| `cuando_usarlo` | sí, ≥1 | «Cuándo usarlo» |
| `cuando_no_usarlo` | no | «Cuándo no usarlo» |
| `entradas`, `salidas` | sí | «Entradas y salidas» |
| `complementarios` `[{id, motivo}]` | no | «Sistemas complementarios» |
| `decide_la_persona` | no | sección «Lo que decide la persona» del README |
| `limites` `{reglas, detenerse}` | no (recomendado) | `LIMITES.md` del núcleo: reglas numeradas y «Cuándo detenerse y preguntar» (al menos una de cada); sin él, reglas genéricas y un aviso |
| `permisos` `{rutas: {protegidas, fuera_de_ia}, acciones: {agente, solo_persona}}` | no | `permisos` del manifiesto y bloque de `PERMISOS.md` (núcleo); sin él, vacío (solo lo implícito de memorias y fichas). `decide_la_persona` va también a «Por qué» de `PERMISOS.md` |
| `proceso` `[{fase, titulo?, condicion?, objetivo, entradas?, pasos, criterio_salida, resuelve, skills?}]` | no | pieza `proceso`: `proceso/<fase>.md`, en el orden dado |
| `skills` `[{nombre, titulo?, descripcion, resuelve, cuando, pasos, resultado?}]` | no | pieza `skills`: `skills/<nombre>/SKILL.md` |
| `fichas` `{tipo: {prefijo?, inicial, estados \| status_validos, solo_humano?, espera_humano?, comandos?, carpeta?, secciones?}}` | no | pieza `plantillas` y `fichas` del manifiesto; sin `prefijo`, se propone uno libre |
| `ajustes` | no | `ajustes` del manifiesto (valores por defecto que cada proyecto cambia en su `ajustes.json`) |
| `ejemplos` `[{nombre, titulo, pedido, recorrido, resultado}]` | no | pieza `ejemplos`: `ejemplos/<nombre>.md` |
| `memorias` `{recordar, no_recordar}` | no (recomendado) | `MEMORIAS.md` del núcleo: «Qué recordar» y «Qué no recordar»; sin él, un texto genérico y un aviso |
| `piezas_extra` | no | piezas sin generador (`componentes`, `herramientas`, `andamiaje`, `referencia`, `pruebas`) que se añaden con marcadores para completar en modo guiado |

`cambios` (`CHANGELOG.md` con la versión 0.1.0) se crea siempre.

### Comprobaciones antes de escribir

Errores: campos obligatorios, nomenclatura del id y del título, familia, id existente o que choca con otro, frases de
activación, problemas repetidos o mal formados, `derivar_a` y `complementarios` que no son sistemas del catálogo, `resuelve`
que cita problemas inexistentes, fases que citan skills inexistentes, prefijos de ficha inválidos o ya usados, descripciones
de skill con salto de línea o « #», piezas extra desconocidas y marcadores `{{…}}`.

Avisos: más de 5 problemas, problemas que no cubre ninguna fase ni skill, skills sin `resuelve`, sistema sin proceso ni skills
y piezas recomendadas para la familia que faltan.

## Pendientes

`generar pendientes <id>` revisa cualquier sistema del catálogo (generado o no) y devuelve:

- `errores`: los de `validar`, incluida la nomenclatura;
- `marcadores`: cada `{{…}}` con `archivo`, `linea` y el texto de la línea (las plantillas de fichas en `plantillas/` los
  llevan a propósito y no cuentan);
- `faltan_recomendadas` y `avisos`;
- `listo`: sin errores ni marcadores;
- `siguiente`: una sola acción concreta, por prioridad: marcadores del núcleo, errores, otros marcadores, piezas
  recomendadas, avisos y, al final, cerrar (CHANGELOG, versión y pruebas).

La secuencia de comandos, como skill para quien crea sistemas: [`skills/crear-sistema/SKILL.md`](skills/crear-sistema/SKILL.md).
