---
fase: diagnosticar
resuelve: [secretos-en-el-codigo, archivos-de-secretos-versionados]
skills: [escanear-secretos]
---

# Fase: diagnosticar

## Objetivo

Conocer los hallazgos que ya existían en las rutas del pedido, para no confundirlos con los propios y para detectar a tiempo un secreto real heredado.

## Entradas

- El pedido y las rutas que va a tocar.
- Los ajustes efectivos (`raices`, `excluir`, `permitir`).

## Pasos

1. Aplica la skill `escanear-secretos` sobre las rutas del pedido (o con `--git` si va a terminar en commit).
2. Anota cada hallazgo previo por ruta y línea, nunca con su valor.
3. Si algún hallazgo previo parece un secreto real, no sigas: pasa a `atender-incidente` antes de implementar.
4. Si el pedido requiere credenciales nuevas (un cliente de un servicio externo, un despliegue), decide ya el nombre de cada variable de entorno.

## Criterio de salida

- Tienes la lista de hallazgos previos (puede estar vacía) y ninguno pendiente de tratar como incidente.
- Sabes qué variables de entorno necesitará el cambio.
