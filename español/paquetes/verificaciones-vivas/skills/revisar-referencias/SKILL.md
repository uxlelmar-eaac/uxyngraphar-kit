---
name: revisar-referencias
description: Busca en todo el trabajo de uxyngraphar las anclas a archivos de código que ya no existen y los ids de fichas citados que no existen, con una sugerencia de dónde está ahora el archivo.
resuelve: [referencias-rotas]
---

# Revisar referencias

## Cuándo usarla

- Tras una refactorización que mueve o renombra archivos.
- Tras retirar o borrar fichas que otras citaban.

## Pasos

1. Ejecuta `python3 $P/scripts/vivas.py anclas vinculos`.
2. `anclas` recorre los `.md` de `uxyngraphar/trabajo/`: toma los campos de `campos_ancla` (`ancla`, `anclas`, `anclas_codigo`) y las rutas entre comillas invertidas bajo cualquier título que contenga «ancla»; ignora las que llevan `<`, `>`, `*`, `…`, llaves o son URL.
3. Un ancla rota sale como `media: ancla rota: src/orders/orders.service.ts (¿ahora en src/billing/orders.service.ts?)` cuando hay un archivo de código con el mismo nombre en otro sitio.
4. `vinculos` busca ids `XXX-AAAAMMDD-slug` en el trabajo que no corresponden a ninguna ficha de los paquetes instalados: `media: id colgante: RUT-20260101-pedidos-viejos — archivo:línea`.
5. Un id de un paquete que no está instalado también sale como colgante: compruébalo antes de proponer borrarlo.

## Resultado

- Las anclas rotas (con sugerencia si la hay) y los ids colgantes, con la ficha que los cita.
