# Actualizar el núcleo en un proyecto alineado

Guía para cuando el pack publica una versión nueva y el proyecto ya tiene un sistema adoptado.

## Principio

Formato de trabajo **no bloqueante**: la actualización fluye siempre **pack → proyecto**, nunca al revés, y **nunca toca contenido del proyecto** (clase C) ni sobrescribe plantillas rellenadas (P) o índices (M). Ver [congelamiento.md](../00-nucleo/congelamiento.md).

## Garantías

Una actualización nunca deja un proyecto roto ni desvinculado de uxyngraphar. Cada una se cumple por código y tiene su prueba:

| Garantía | Cómo se cumple |
|---|---|
| **Tu contenido no se toca** | Fichas, instrucciones, rutas, espejo y `uxyngraphar.config.json` (clases C y P) nunca se sobrescriben; si cambió en ambos lados, la versión nueva queda al lado como `.uxyngraphar-nuevo`. |
| **Todo o nada** | La actualización es una transacción: antes de tocar cada archivo se guarda su copia y se anota en un diario (`_diario.jsonl` en `.uxyngraphar-respaldo/<fecha>/`). Si falla, o la cortas con Ctrl+C, se deshace en el acto. |
| **Un corte brusco se repara solo** | Si el proceso muere (apagón, terminal cerrada), el diario queda abierto: la siguiente actualización, o `doctor.py --fix`, deja el proyecto exactamente como estaba antes de empezar. `doctor.py` lo avisa mientras tanto. |
| **Si la versión nueva no funciona, no se queda** | Tras actualizar se ejecutan las herramientas del proyecto tal como las llaman los ganchos y el CI (prueba de humo). Si alguna deja de arrancar o pierde una opción, se deshace la actualización y se explica por qué. Solo cuenta lo que funcionaba antes de actualizar. |
| **Los ganchos y el CI antiguos siguen valiendo** | Los scripts y opciones del [contrato de compatibilidad](../scripts/nucleo/contrato.py) no se quitan nunca (la lista solo crece; un renombre deja el nombre viejo como alias). |
| **Saltar versiones funciona** | Pasar de cualquier versión a la última aplica en orden las [migraciones](../scripts/nucleo/migraciones.py) pendientes (claves de configuración, archivos movidos…), cada una una sola vez (el lock las registra). |
| **Lock dañado o perdido** | Si `.uxyngraphar.lock` no se puede leer, se usa su copia del último respaldo; sin copia, nada se sobrescribe (todo cuenta como conflicto) y la actualización lo vuelve a escribir sano. |
| **Cada versión se prueba contra las anteriores** | Antes de publicar, el CI instala cada versión publicada en un proyecto de prueba con contenido propio, lo actualiza a la nueva y comprueba todo lo anterior (`_compartido/probar-actualizaciones.py` en el repo fuente). Si un salto falla, la versión no se publica. |
| **Se puede deshacer** | Cada actualización deja su copia en `.uxyngraphar-respaldo/<fecha>/`: `respaldos.py restaurar actualizacion/<fecha> --aplicar` (ver [respaldos.md](respaldos.md)). |

Lo único que no se aplica solo es un salto **MAYOR** (paso 4 del procedimiento): cambia reglas del protocolo y necesita tu aprobación explícita.

## Procedimiento

1. Con un clon actualizado de uxyngraphar, **simula** (no escribe nada):

   ```bash
   python3 docs/scripts/actualizar-pack.py RUTA/AL/PACK
   ```

(En Windows: `py -3` en lugar de `python3`.)

   Compara tres versiones de cada archivo: la **base** (`docs/.uxyngraphar.lock`), la **local** y la **nueva**. Resultado por archivo: `añadir`, `reemplazar`, `conflicto`, `modificado-local`, `plantilla-cambiada` o `retirado`.
2. Revisa el informe. Árbol de git limpio, y aplica:

   ```bash
   python3 docs/scripts/actualizar-pack.py RUTA/AL/PACK --apply
   ```

   Respaldo previo en `.uxyngraphar-respaldo/<fecha>/` (deshacer entera: `respaldos.py restaurar actualizacion/<fecha> --aplicar`; ver [respaldos.md](respaldos.md)); escritura atómica con reversión si algo falla; actualiza el lock y anota en `90-archivo/cambios-pack.md`.
3. **Conflictos** (cambió en ambos lados): el actual no se toca; la versión nueva queda como `<archivo>.uxyngraphar-nuevo`. Si el núcleo se había editado sin respaldo, `--restaurar-nucleo` lo devuelve a la versión del pack (el respaldo conserva la tuya).
4. **Salto MAYOR** (p. ej. 2.x → 3.0): exige una instrucción aprobada con el plan de migración y `--migracion-aprobada <id>`. Sin ella no se aplica.
5. Plantillas P / índices M con novedades: el informe las lista como `plantilla-cambiada`; intégralas a mano.
6. Cierra: `python3 docs/scripts/verificar-nucleo.py` y `validar-documentacion.py`; `--evo` en el paso 2 crea además la ficha de adopción.

Sin `.uxyngraphar.lock` (proyectos que adoptaron el pack a mano, antes de que existiera el lock) no hay base: toda diferencia es conflicto y no se pisa nada. Tras resolverlas el lock queda creado.

## Alineación inicial

Proyecto sin sistema: [instalacion-docs.md](instalacion-docs.md) (`instalar-pack.py`) y la guía de adopción (`05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md`).

## Actualizar sin comandos (doble clic)

En el repo de uxyngraphar, en cualquier sistema: `python3 actualizar.py RUTA_PROYECTO` (`--si` para no preguntar; admite varias carpetas). Detecta los packs instalados, muestra el plan, respalda en `.uxyngraphar-respaldo/`, actualiza el núcleo y añade las protecciones que versiones nuevas incorporan (workflow de CI, reglas `deny`, `.gitignore`, `.gitattributes`, lock). Tu contenido no se toca. Un salto de versión **mayor** se rechaza: sigue la sección anterior con instrucción aprobada.

Desde el propio proyecto, `actualizar-pack.py RUTA_PACK --apply` hace lo mismo; `doctor.py --fix` repite solo la parte de protecciones.
