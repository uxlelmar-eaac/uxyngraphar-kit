# Ajustes locales (R-25)

Aplicar en **este proyecto** una mejora del sistema documental sin esperar a que llegue al pack y **sin editar el núcleo**. El ajuste es contenido del proyecto (`docs/97-ajustes-locales/`), así que ninguna actualización lo pisa ni choca con él.

## Cuándo

Una ficha `EVO-*` de `46-evolucion-documentacion/` está **aprobada** (`approved`) y la quieres usar ya: un paso que falta en una guía, una regla de plantilla, un matiz del protocolo. Si la mejora es de tu producto (código, bug, deuda), no es un ajuste: va a `45-mejoras-propuestas/`.

## Cómo (solo personas)

```bash
# 1. Escribe la regla local en un archivo (lo que el agente debe hacer distinto o además)
# 2. Crea el ajuste: qué EVO aplica y qué archivo del núcleo complementa (uno o varios --a)
python3 docs/scripts/ajustes.py crear --evo EVO-20261030-paso-revision --a 10-guias/sync-documentacion-pr.md --texto regla.md
python3 docs/scripts/ajustes.py listar
```

Qué hace `crear`: escribe `97-ajustes-locales/AJ-AAAAMMDD-slug.md` con la regla, el archivo que complementa y su **huella**; apunta `ajuste_local: AJ-…` en la EVO y pone el ajuste en la tabla de `97-ajustes-locales/INDICE.md`. El núcleo no cambia.

## Qué hace el agente

- Antes de seguir un archivo del núcleo mira la tabla de `97-ajustes-locales/INDICE.md`. Si un ajuste activo lo complementa, lo lee y, **donde se contradigan, manda el ajuste** (solo en este proyecto).
- `contexto.py` lo trae solo: si la instrucción cita el archivo en `lectura_minima`, el ajuste aparece justo detrás.
- No crea, edita ni retira ajustes. Si cree que hace falta uno, registra una ficha `EVO-*`.

## Al actualizar el pack

```bash
python3 docs/scripts/ajustes.py verificar
```

| Aviso | Qué significa | Qué hacer |
|-------|---------------|-----------|
| el archivo «cambió con una actualización» | La versión nueva tocó el archivo que el ajuste complementa | Léelo. Si el ajuste sigue haciendo falta: `ajustes.py revisado AJ-ID`. Si no: `retirar` |
| «el CHANGELOG ya cita EVO-…» | La mejora llegó al pack | `ajustes.py retirar AJ-ID --motivo "incluida en X.Y.Z"` |
| el archivo «ya no existe» | El pack lo movió o lo quitó | Retira el ajuste o vuelve a crearlo sobre el archivo nuevo |

`doctor.py` muestra el mismo aviso. Un ajuste retirado queda como historia (`status: retirado`); con el tiempo puedes pasarlo a la memoria (R-24).

## Límites

- Solo desde una EVO aprobada; solo complementa archivos del pack (reglas, protocolos, guías, plantillas), nunca `95-memoria/`, otro ajuste ni una ficha.
- No relaja los controles: un ajuste no puede apagar la puerta (`controlar.py`), la protección del núcleo ni R-20. Eso se cambia en `uxyngraphar.config.json` o en el pack.
- Si muchos proyectos aplican el mismo ajuste, es una buena señal para el pack: envía la ficha EVO de la que nace (marcada `aplicada_en_local`) con [envio-sugerencias.md](envio-sugerencias.md). El ajuste en sí no se envía.
