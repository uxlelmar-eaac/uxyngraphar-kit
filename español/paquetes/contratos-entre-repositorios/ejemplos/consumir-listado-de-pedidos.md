# Caso: el cliente web consume el listado de pedidos de la API

## Pedido

En el repositorio `web` (cliente): «Muestra el historial de pedidos usando el endpoint de la API». La API vive en `../api`; `ajustes.json` de `web` tiene `{"repo": "web", "otros_repos": ["../api"]}`.

## Recorrido

**identificar-contrato.** `fichas.py listar contrato` en `web` no tiene nada para pedidos. El `REGISTRO.md` de `../api` lista `orders.list | proveedor | GET /orders | v1 | api | uxyngraphar/trabajo/rutas-de-api/orders/RUT-20260115-get-orders.md | vigente`. Rol de `web`: `consumidor`; id compartido: `orders.list` (el mismo). Cambio compatible.

**registrar-contrato → crear-contrato** (skill):

```
python3 $P/scripts/comun/fichas.py nueva contrato --slug orders-list --titulo "Listado de pedidos"
```

```yaml
id_compartido: orders.list
rol: consumidor
method: GET
path: /orders
version: v1
proveedor: api
ficha_proveedor: ../api/uxyngraphar/trabajo/rutas-de-api/orders/RUT-20260115-get-orders.md
```

«Forma (resumen)»: «Entrada: `page`. Salida: lista paginada; tipos generados en `src/generated/api.ts`». Sin copiar la ficha del proveedor. Lado técnico (`referencia/contratos-api.md`): la respuesta se adapta en `src/modules/orders/reception/orders.reception.ts`.

```
$ python3 $P/scripts/contratos.py registro
uxyngraphar/trabajo/contratos-entre-repositorios/REGISTRO.md
```

**sincronizar-repositorios.** El contrato está `propuesto`; la persona lo revisa y lo marca `vigente --humano`. Después, skill `comparar-repositorios`:

```
$ python3 $P/scripts/contratos.py comparar
contratos: 0 divergencias, 0 avisos
```

El proveedor ya tenía el endpoint fusionado: el PR de `web` puede cerrarse. Lista de `referencia/sincronizar.md` revisada.

**verificar.**

```
$ python3 $P/scripts/verificar-contratos.py
contratos-entre-repositorios: 0 errores, 0 avisos
```

## Resultado

- Contrato `orders.list` de consumidor en `web`, con el mismo id que en `api` y la ficha del proveedor citada.
- Registro regenerado y comparación sin divergencias.
