---
id: auto.01.rutas-vivas
stack: [cliente]
---

# 01: rutas-vivas

## Fuente

`15-rutas/`: cada ficha tiene `id` estable (`modulo.recurso.accion`),
método, path y archivos ancla.

## Valida

Que cada ruta documentada existe en el código, responde y coincide en
método + path.

## Procedimiento

1. Leer el INDICE de `15-rutas/` y extraer método + path de cada ficha.
2. Levantar el proyecto en modo prueba y pedir cada ruta.
3. Comparar estado HTTP real contra lo declarado en la ficha.

## Aceptación

- [ ] Toda ficha tiene su ruta respondiendo (2xx/3xx o el estado
  documentado en la ficha).
- [ ] Cero rutas documentadas sin contraparte en el código.
- [ ] Cero rutas en el código (públicas) sin ficha.

## Salida

Tabla: `id | método+path | estado real | veredicto`.
