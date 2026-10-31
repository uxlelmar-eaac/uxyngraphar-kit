# Protocolo — reglas del proyecto (`96-reglas-proyecto/`)

Reglas que **el equipo** pone a su propio código (convenciones, prohibiciones, patrones obligatorios). No son reglas del núcleo (R-xx) ni las cambian: el núcleo solo dice dónde están y cómo se aplican. La carpeta llega vacía; cada proyecto escribe las suyas.

## Qué contiene

| Archivo | Qué es |
|---------|--------|
| `INDICE.md` | Una fila por regla activa (id, nivel, aplica_a, resumen). **Lo único que el agente lee por defecto.** |
| `RP-NNN.md` | Una regla, desde [_PLANTILLA-regla.md](_PLANTILLA-regla.md). Contenido del proyecto: ninguna actualización lo toca. |
| `EX-AAAAMMDD-slug.md` | Ficha de excepción, solo con `reglas_proyecto.excepciones: "ficha_aparte"` ([_PLANTILLA-excepcion.md](_PLANTILLA-excepcion.md)). |

## Cómo las usa el agente (económico en tokens)

1. Al **crear** una instrucción: mira `INDICE.md` y respeta las reglas cuyo `aplica_a` toca sus anclas.
2. Al **ejecutarla**: `contexto.py <id>` imprime solo las reglas activas que tocan `anclas_codigo` (id, nivel y resumen; el cuerpo solo de las bloqueantes). No abre más reglas.
3. Si una regla no puede cumplirse: la declara en la instrucción (`excepciones_reglas: ["RP-NNN: motivo"]`) y espera a que una persona la apruebe. Nunca se la salta en silencio.

## Ciclo de vida

- `status: activa` → se aplica. `status: retirada` → deja de aplicarse (el archivo se conserva como historia).
- Crear, editar, mejorar o retirar una regla: el agente **solo** con una instrucción aprobada por una persona que tenga el archivo de la regla en `anclas_codigo` (o `docs/96-reglas-proyecto/` entero). Con `cambios_reglas: "solo_humano"` el agente no puede tocarlas (reglas deny); las cambia una persona.
- Al cerrar esa instrucción, `decisiones.py cerrar` regenera `INDICE.md`.

## Niveles y control (`controlar.py`)

- `nivel: bloqueante` + `comprobacion_prohibido` / `comprobacion_obligatorio` (regex por línea / en el archivo): si un archivo de código del cambio que cae en `aplica_a` incumple, **el commit se bloquea**, salvo excepción aprobada. `nivel: aviso`: solo avisa.
- Sin `comprobacion_*` la regla no se puede verificar sin IA: vale como instrucción para el agente y para la revisión humana.
- También bloquea: una excepción en una instrucción sin aprobar, y cambiar reglas sin una instrucción aprobada que las ancle.
- El nivel del control se fija en `niveles.reglas_proyecto` de `uxyngraphar.config.json` (por defecto `bloqueante`).

## Excepciones (`reglas_proyecto.excepciones` en `uxyngraphar.config.json`)

| Valor | Cómo se aprueba una excepción |
|-------|------------------------------|
| `en_instruccion` (por defecto) | Declarada en `excepciones_reglas` de la instrucción; queda aprobada cuando una persona pasa la instrucción a `approved`. Vale solo para esa instrucción. |
| `ficha_aparte` | Además, una ficha `EX-*.md` en esta carpeta con `status: aprobada`, `regla` e `instruccion`, aprobada por una persona. |
| `prohibidas` | No se admite ninguna: hay que cumplir la regla o cambiarla. |

Detalle de la configuración: [configuracion-uxyngraphar.md](../10-guias/configuracion-uxyngraphar.md).
