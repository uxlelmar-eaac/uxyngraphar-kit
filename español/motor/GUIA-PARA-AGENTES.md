# Guía para agentes: crear un sistema

El método con que se crean todos los sistemas del catálogo, escrito como proceso para un agente de IA. Las normas que aplica
están en [`GUIA-DE-SISTEMAS.md`](GUIA-DE-SISTEMAS.md) (diseño), [`NOMENCLATURA.md`](NOMENCLATURA.md) (nombres),
[`ESPECIFICACION.md`](ESPECIFICACION.md) (contrato) y [`GENERADOR.md`](GENERADOR.md) (especificación y comandos).
Desde `español/`, `U="python3 motor/uxyngraphar.py"` (instalado, basta `uxyngraphar`).

## Límites

1. **Solo con el generador.** Nunca copies `_base` ni otro sistema a mano: `$U generar desde` o `$U crear`.
2. **Solo en el catálogo.** Se crea y edita en `sistemas-de-gobernanza/<id>/` del kit; nunca en `uxyngraphar/sistemas-de-gobernanza/` de un proyecto.
3. **Lee JSON, no texto.** Usa `--json` en `generar`, `validar` y `crear` y decide con sus campos (`errores`, `listo`, `siguiente`).
4. **Sin marcadores al terminar.** Un sistema se entrega con `generar pendientes` en «listo».
5. **Una persona decide el alcance.** Si dudas de qué cubre o qué deja fuera, pregunta antes de generar.

## Fase 1: diseñar

Objetivo: el alcance cabe en pocas líneas y no pisa a otro sistema.

1. Lista el catálogo: `$U validar --json` (ids, títulos) y lee el `SISTEMA.md` de los que se parezcan.
2. Pasa la prueba de especialización de `GUIA-DE-SISTEMAS.md` §2: una frase sin «y además», problemas que comparten proceso,
   un solo perfil de trabajo, 5 problemas como máximo.
3. Escribe los problemas como síntomas (`capas-mal-importadas`, no `revisar-capas`) y, para cada tema que no cubres, a qué
   sistema se deriva (`derivar_a`) o `null`.
4. Elige las piezas con la tabla de `GUIA-DE-SISTEMAS.md` §3 y la familia (`validar --completitud` dice las recomendadas).
5. Decide las memorias (`memorias` de la especificación → `MEMORIAS.md`, núcleo obligatorio): qué dato del proyecto
   necesita el sistema y se pierde entre conversaciones, y qué no se memoriza porque ya vive en fichas, código u otro sistema.
6. Decide límites y permisos (`limites` y `permisos` de la especificación → `LIMITES.md`, `PERMISOS.md` y `permisos` del
   manifiesto, núcleo obligatorio): reglas duras, cuándo detenerse, qué acciones son solo de la persona y qué rutas no toca la IA.

Criterio de salida: id, título, familia, problemas, fuera de alcance, memorias, límites, permisos y piezas decididos; si algo es dudoso, la persona lo confirmó.

## Fase 2: generar

Objetivo: el sistema existe en el catálogo y valida.

- **Completo** (recomendado si la fase 1 está clara):
  1. `$U generar plantilla --id <id> --familia <f> > /tmp/<id>.json` y rellénala (borra lo que no uses).
  2. `$U generar desde /tmp/<id>.json --json`: corrige la especificación hasta que `errores` esté vacío y revisa `avisos`.
  3. `$U generar desde /tmp/<id>.json --aplicar --json`: `aplicado: true`.
- **Guiado:** `$U crear <id> --titulo "…" --familia <f> --piezas a,b --json`.

Criterio de salida: `sistemas-de-gobernanza/<id>/` existe.

## Fase 3: completar

Objetivo: no queda nada por rellenar.

1. `$U generar pendientes <id> --json`.
2. Haz lo que diga `siguiente` (un marcador `archivo:linea`, un error, una pieza recomendada) editando solo `sistemas-de-gobernanza/<id>/`.
   Si cambias `sistema.json`, ejecuta `$U indice-sistema <id>`.
3. Repite hasta `listo: true` y revisa los `avisos` que queden: corrígelos o explica a la persona por qué se quedan.

Escribe para quien activará el sistema en cualquier proyecto: fases con criterio de salida verificable, skills de una acción
con su comando o archivo exacto, límites pocos y comprobables, un ejemplo real recorrido fase a fase.

Criterio de salida: `listo: true`.

## Fase 4: probar

1. `$U validar <id> --json`: `errores` vacío.
2. Si tiene la pieza `pruebas`: `$U sincronizar-comun` (copia local de `scripts/comun/`) y `python3 -m unittest discover -s sistemas-de-gobernanza/<id>/pruebas -t sistemas-de-gobernanza/<id>/pruebas`.
3. Si tiene scripts propios, cada uno documentado en `HERRAMIENTAS.md` y probado.

Criterio de salida: validación y pruebas en verde.

## Fase 5: cerrar

1. `CHANGELOG.md` con la versión del manifiesto (un sistema nuevo es 0.1.0; para publicarlo, la persona decide `$U version <id> …`).
2. Si otro sistema del catálogo debe derivar a este, propón el cambio en su «Fuera de alcance» (y su CHANGELOG y versión).
3. Resume a la persona: qué cubre, qué deja fuera, piezas, avisos que quedan y cómo instalarlo (`$U instalar <id> --repo …`).

## Cuándo detenerse y preguntar

- El alcance solapa con un sistema existente o no pasa la prueba de especialización.
- Hacen falta más de 5 problemas.
- El sistema necesitaría cambiar otro sistema del catálogo.
- `generar desde` sigue con errores que no se resuelven sin cambiar el alcance acordado.
