# Rutas de API

Mantiene una ficha viva por endpoint HTTP —método, ruta, autenticación, entrada, salida, pipeline y archivos ancla— que se actualiza en la misma tarea que cambia la API.

## Qué resuelve

El contrato de una API se dispersa entre controladores, DTO, middlewares y pruebas. Sin un sitio único, cada cambio obliga a releer el código para saber qué recibe un endpoint, quién puede llamarlo y qué errores devuelve, y los clientes descubren las roturas en producción. Este paquete da a cada endpoint una ficha corta con su contrato visto desde el cliente y comprueba que no haya duplicadas, que tenga los campos clave y que sus anclas existan.

## Problemas que cubre

- `endpoints-sin-ficha`: endpoints del código sin ficha que describa su contrato.
- `fichas-de-ruta-desfasadas`: fichas que ya no coinciden con el endpoint o con anclas que ya no existen.
- `rutas-documentadas-dos-veces`: dos fichas activas para el mismo método y ruta.
- `seguridad-de-endpoint-implicita`: endpoints sin `auth` ni `roles` declarados, o públicos sin justificar.
- `endpoints-retirados-sin-rastro`: endpoints eliminados o en desuso sin `retirada`/`deprecada` ni alternativa.

## Fuera de alcance

- Contratos entre el repositorio que sirve la API y los que la consumen: `contratos-entre-repositorios`.
- Páginas y rutas de la interfaz: `paginas-de-interfaz`.
- Encontrar de forma automática endpoints del código sin ficha: `verificaciones-vivas`.
- Capas internas del módulo que implementa el endpoint: `arquitectura-monolitica-por-capas`.
- Generar o publicar OpenAPI y clientes derivados: no lo cubre el kit.

## Cuándo usarlo

- Al crear, cambiar o eliminar un endpoint HTTP.
- Antes de tocar un endpoint existente, para saber qué contrato hay que respetar.
- Al documentar una API existente endpoint a endpoint.

## Cuándo no usarlo

- En proyectos sin API HTTP propia (solo consumen APIs de terceros).
- Para APIs que ya se documentan con una especificación generada que el equipo trata como fuente única: la ficha duplicaría esa fuente.

## Entradas y salidas

- Entradas: el código del endpoint (controlador, caso de uso, DTO, pruebas), el pedido y los ajustes `campos_obligatorios` y `clave_unica`.
- Salidas: fichas `RUT-…` en `uxyngraphar/trabajo/rutas-de-api/<modulo>/` y el informe de `verificar-rutas.py`.

## Paquetes complementarios

- `contratos-entre-repositorios`: el consumidor cita la ficha del proveedor en lugar de copiarla.
- `paginas-de-interfaz`: las páginas enlazan los endpoints que consumen.
- `verificaciones-vivas`: lista los endpoints del código que aún no tienen ficha.
- `arquitectura-monolitica-por-capas`: el pipeline de la ficha recorre las capas del módulo.
