# Caso: página de aterrizaje de cobros para tiendas

## Pedido

«Usa el paquete paginas-de-aterrizaje-bento: haz la página de lanzamiento del servicio de cobros para tiendas pequeñas. Que se den de alta.» Ajustes por defecto: 4 columnas, 5–9 celdas, títulos de 6 palabras.

## Recorrido

**redactar-brief.** No hay fichas previas. Se abre la ficha:

```
python3 $P/scripts/comun/fichas.py nueva landing --slug cobros --titulo "Cobros para tiendas"
…/trabajo/paginas-de-aterrizaje-bento/pendientes/LAN-20261106-cobros.md
```

Objetivo: «crear una cuenta gratis». Audiencia: dueños de tiendas pequeñas que llegan desde un anuncio y dudan entre esto y el datáfono del banco. `ruta_pagina: /cobros`.

**disenar-mosaico.** Primer intento con `componer-mosaico` y `escribir-celda`, repitiendo el CTA al final como `primario` en una celda `2x1`:

```
| 1 | 2x2 | 1 | Cobra en 2 minutos | Sin contratos ni permanencia            | primario | img: panel de cobros en un móvil |
| 2 | 2x1 | 2 | Pagos en 30 países | Monedas locales y conversión automática | -        | icono |
| 3 | 1x1 | 3 | Soporte 24/7       | Personas reales                         | -        | - |
| 4 | 1x1 | 4 | Seguro             | Cifrado de extremo a extremo            | -        | - |
| 5 | 2x1 | 5 | Empieza hoy        | Cuenta gratis en un minuto              | primario | - |
```

En `borrador` la verificación avisa:

```
python3 $P/scripts/verificar-bento.py
aviso: pendientes/LAN-20261106-cobros.md: debe haber exactamente un CTA primario (hay 2)
aviso: pendientes/LAN-20261106-cobros.md: la suma de áreas (10) no llena filas de 4 columnas: hay huecos
bento: 0 errores, 2 avisos
```

Corrección: la celda 5 pasa a banda `4x1` (4+2+1+1+4 = 12, tres filas) y su CTA a `secundario` (es la misma acción repetida, no otro CTA primario). Orden móvil: 1 → 5, sin excepciones. Ficha a `en-curso`:

```
python3 $P/scripts/comun/fichas.py estado LAN-20261106-cobros en-curso
python3 $P/scripts/verificar-bento.py
bento: 0 errores, 0 avisos
```

**construir.** Las cinco celdas se escriben en el DOM en orden de prioridad y se colocan con `grid-column`/`grid-row`. La imagen de la celda 1 lleva `fetchpriority="high"` y `aspect-ratio`; el icono de la celda 2, `aria-hidden`. El CTA primario es el botón existente del proyecto, que enlaza a `/alta`. `archivos: [src/pages/cobros.tsx, src/pages/cobros.module.css]`.

**revisar-publicacion.** Al pasar a `revision` sin marcar la checklist:

```
python3 $P/scripts/comun/fichas.py estado LAN-20261106-cobros revision
python3 $P/scripts/verificar-bento.py
error: en-progreso/LAN-20261106-cobros.md: checklist incompleta en «revision»: Contraste AA en textos y controles; Foco visible …
bento: 1 errores, 0 avisos
```

Con `comprobar-checklist` se revisa cada punto en el navegador (Lighthouse: contraste correcto, CLS 0.02; Tab sigue 1 → 5; móvil a 375 px con la protagonista primera) y se marcan las ocho casillas. `verificar-bento.py` vuelve a `bento: 0 errores, 0 avisos`. El agente no puede publicar:

```
python3 $P/scripts/comun/fichas.py estado LAN-20261106-cobros publicada
error: «publicada» solo lo asigna una persona (usa --humano si eres tú)
```

## Resultado

- Ficha `LAN-20261106-cobros` en `revision` con mosaico de 5 celdas sin huecos, un único CTA primario y checklist completa.
- La página en `src/pages/cobros.tsx`; la persona la revisa y la publica con `--humano`.
