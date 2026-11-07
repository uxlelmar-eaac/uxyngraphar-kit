# Límites

Se cumplen en todo el código que el agente escribe o modifica. Solo una persona puede cambiar los ajustes o las exenciones.

1. **Límite de líneas.** Ningún archivo de código supera `limite_lineas` (350) líneas físicas. Si un cambio lo supera, se divide por responsabilidad con **nombre relacional** (`order-service.ts` → `order-service.pricing.ts`, `order-service.validation.ts`). Exenciones solo las declara una persona en `exenciones_lineas`.
2. **Nombres autoexplicativos.** Cada identificador dice qué es y para qué sirve, con unidad o dominio cuando aplica (`timeoutMs`, `isActive`, `ORDER_STATUS.SHIPPED`), con el casing del lenguaje (`referencia/nombres.md`). Prohibidos `data`, `tmp`, `obj`, `x`, `handle2`; los archivos se nombran por responsabilidad y sin espacios. Comentarios solo para el porqué.
3. **No se debilita la revisión.** El agente no edita `ajustes.json`, ni añade exclusiones o exenciones para que `calidad.py` pase.
4. **Solo lo propio.** Un archivo que ya excedía el límite y que el pedido no toca se avisa, no se divide; un archivo que el agente hizo crecer por encima del límite se divide en la misma tarea.

## Cuándo detenerse y preguntar

- Dividir el archivo exige tocar archivos fuera de lo que pidió la persona (muchos importadores, API pública del módulo).
- Renombrar un identificador genérico heredado obliga a cambiar usos fuera de lo que pidió la persona.
- `calidad.py` marca archivos generados o de terceros que no están en `excluir`: la persona decide si excluirlos.
