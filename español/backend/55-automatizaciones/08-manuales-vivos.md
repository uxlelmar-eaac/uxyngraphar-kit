---
id: auto.08.manuales-vivos
stack: [servidor]
---

# 08: manuales-vivos

## Fuente

`30-manuales/` (`despliegue.md`, `incidentes.md`).

## Valida

Que los pasos documentados funcionan (dry-run, sin efectos reales).

## Procedimiento

1. Extraer comandos y pasos de cada manual.
2. Ejecutarlos en modo simulación o ambiente de prueba.

## Aceptación

- [ ] Cero comandos inexistentes o con sintaxis rota.
- [ ] Cero pasos que referencian rutas, servicios o archivos que no existen.

## Salida

Lista: `manual | paso | pasa / falla | motivo`.
