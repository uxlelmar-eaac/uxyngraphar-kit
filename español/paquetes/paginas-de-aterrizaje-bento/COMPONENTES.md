# Componentes

Las piezas que define el paquete. Viven en la ficha de página (`plantillas/landing.md`).

## Ficha de página

Ficha `LAN-<fecha>-<slug>` en `uxyngraphar/trabajo/paginas-de-aterrizaje-bento/<estado>/`, una por página. Estados:

| Status | Carpeta | Quién lo pone | Qué comprueba `verificar-bento.py` |
|--------|---------|---------------|------------------------------------|
| `borrador` | `pendientes` | agente | fallos del mosaico como avisos |
| `en-curso` | `en-progreso` | agente | fallos del mosaico como errores |
| `revision` | `en-progreso` | agente | mosaico y checklist completa; espera a la persona |
| `publicada` | `completadas` | persona (`--humano`) | mosaico y checklist completa |
| `archivada` / `cancelada` | `archivadas` / `canceladas` | cualquiera | nada |

## Rejilla

`columnas` columnas (4 por defecto). Las celdas ocupan `ancho x alto` de entre `tamanos` (`1x1`, `2x1`, `1x2`, `2x2`, `4x1`); la suma de áreas es múltiplo de `columnas`, de modo que no quedan huecos.

## Celda

Fila de la tabla «Mosaico»: `| # | Tamaño | Prioridad | Título | Mensaje | CTA | Medio |`. Dice una sola cosa. Entre `celdas_min` y `celdas_max` por página.

## Prioridad y protagonista

Entero único 1..n por celda. La prioridad 1 es la protagonista: la celda de mayor área (como mucho `max_2x2` celdas `2x2`). La prioridad fija también el orden en el DOM, el apilado móvil y el orden de tabulación.

## CTA primario

La acción del «Objetivo». Exactamente una celda lleva `primario`; las demás, `secundario` o `-`.

## Medio

`-`, `img: <alt>`, `video: <descripción>` o `icono` (decorativo, `aria-hidden`). Una imagen o vídeo sin texto es un error.

## Orden móvil

Sección de la ficha: el apilado en pantallas estrechas, por prioridad 1 → n, con las excepciones justificadas.

## Checklist de publicación

Ocho casillas de la ficha (contraste, foco y orden, alt, movimiento reducido, carga prioritaria, sin saltos de diseño, tres tamaños, CTA). En `revision` y `publicada` todas marcadas. Ver `referencia/checklist-publicacion.md`.
