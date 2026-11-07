---
name: crear-espejo
description: Crea el espejo de un archivo o carpeta de código con espejo.py nuevo y lo rellena con su rol, responsabilidades, interacciones y puntos de extensión, sin copiar el código.
resuelve: [codigo-sin-espejo, espejos-que-copian-codigo]
---

# Crear espejo

## Cuándo usarla

- Se crea un archivo con lógica relevante o una carpeta de módulo.
- Se toca código que no tiene espejo.

## Pasos

1. Crea el espejo: `python3 $P/scripts/espejo.py nuevo <ruta-del-codigo>`. Imprime la ruta creada; si ya existe, responde `error: ya existe el espejo …` (edítalo en lugar de crearlo).
2. Archivo (`plantillas/archivo.md`):
   - «Rol»: una frase sobre qué hace en el sistema («Calcula el total de un pedido con impuestos y descuentos»).
   - «Responsabilidades»: tres a cinco viñetas.
   - «Interacciones»: una fila por archivo, servicio o tabla con que habla, y cómo (importa, llama por HTTP, emite evento…).
   - «Puntos de extensión»: dónde se toca para cambiar el comportamiento.
3. Carpeta (`plantillas/carpeta.md`): «Propósito», una fila de «Contenido» por elemento relevante y «Fronteras» (depende de / la usan).
4. No pegues código ni firmas completas; nombra funciones solo si son puntos de extensión.

## Resultado

- Un espejo en `uxyngraphar/trabajo/documentacion-espejo/<ruta>` con todas sus secciones escritas y sin código pegado.
