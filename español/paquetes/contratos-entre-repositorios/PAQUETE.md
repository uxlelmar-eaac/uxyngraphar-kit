# Contratos entre repositorios

Mantiene alineados el repositorio que provee una API y los que la consumen: cada contrato tiene un id compartido estable en todos los repositorios, se registra, se compara con los repositorios hermanos y se fusiona en orden (proveedor primero), sin duplicar las fichas del proveedor.

## Qué resuelve

Cuando servidor y cliente viven en repositorios distintos, cada uno documenta la API a su manera: el cliente copia la ficha o el OpenAPI y la copia se desfasa, los nombres no coinciden y un PR del cliente se fusiona antes de que exista el endpoint. Este paquete da a cada contrato un id compartido, una ficha corta en cada lado que cita (no copia) la del proveedor, un registro generado y una comparación automática con el repositorio hermano.

## Problemas que cubre

- `ids-compartidos-inconsistentes`: el mismo contrato con id distinto, mal formado, repetido o renombrado.
- `contratos-divergentes-entre-repositorios`: método, ruta o versión distintos entre consumidor y proveedor, o el proveedor no lo documenta.
- `fichas-del-proveedor-copiadas`: el consumidor copia la ficha u OpenAPI del proveedor en lugar de citarlos.
- `consumidor-fusionado-antes-que-proveedor`: el consumidor fusiona sin que el proveedor haya fusionado.
- `cambios-incompatibles-sin-version`: cambios que rompen consumidores sin versión nueva ni convivencia.

## Fuera de alcance

- La ficha de cada endpoint en el repositorio proveedor: `rutas-de-api`.
- La ficha de la página o del manejador propio del cliente (BFF): `paginas-de-interfaz`.
- Capas e imports dentro de cada repositorio: `arquitectura-monolitica-por-capas`.
- Secretos expuestos en variables públicas del cliente: `secretos-y-credenciales`.
- El script del proyecto que genera tipos desde OpenAPI: no lo cubre el kit.

## Cuándo usarlo

- Al consumir desde un repositorio una ruta que sirve otro.
- Al publicar o cambiar en el proveedor una ruta que consumen otros repositorios.
- Al preparar el PR de un consumidor que depende de un cambio del proveedor.
- Al hacer un cambio incompatible en una API compartida.

## Cuándo no usarlo

- En un único repositorio que sirve y consume su propia API: basta `rutas-de-api`.
- Para APIs de terceros que el equipo no controla.

## Entradas y salidas

- Entradas: las fichas `rutas-de-api` del proveedor (citadas, no copiadas), los ajustes `repo` y `otros_repos`, y el `uxyngraphar/trabajo/` de los repositorios hermanos cuando están al lado.
- Salidas: contratos `CON-…` en `uxyngraphar/trabajo/contratos-entre-repositorios/`, `REGISTRO.md` generado y los informes de `contratos.py comparar` y `verificar-contratos.py`.

## Paquetes complementarios

- `rutas-de-api`: la fuente humana del contrato en el proveedor; `comparar` también busca allí método y ruta.
- `paginas-de-interfaz`: el BFF del cliente lleva ficha de página además de su contrato `rol: bff`.
- `mapa-de-modulos` y `documentacion-espejo`: citan el `id_compartido` en lugar de repetir el contrato.
