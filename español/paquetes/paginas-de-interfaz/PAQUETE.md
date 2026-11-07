# Páginas de interfaz

Mantiene una ficha viva por página o ruta de la interfaz —qué ve el usuario, quién entra, qué datos consume, sus cuatro estados y sus archivos ancla— que se actualiza en la misma tarea que cambia la navegación.

## Qué resuelve

En una interfaz, lo importante de una página está repartido entre el enrutador, las guardas, los hooks de datos y los componentes. Sin una ficha, nadie sabe qué ve el usuario cuando falla la carga, quién puede entrar ni qué endpoints dispara, y cada cambio rompe un estado olvidado. Este paquete da a cada ruta una ficha con esos datos y comprueba que no haya rutas duplicadas, que tengan los campos clave y que sus anclas existan.

## Problemas que cubre

- `paginas-sin-ficha`: rutas de interfaz sin ficha.
- `fichas-de-pagina-desfasadas`: fichas que ya no coinciden con la página o con anclas que ya no existen.
- `estados-de-interfaz-sin-definir`: páginas sin decidir carga, vacío, error y éxito.
- `acceso-a-pagina-implicito`: sesión, roles o redirecciones que solo se ven en el código.
- `rutas-de-interfaz-documentadas-dos-veces`: dos fichas activas para la misma ruta, o rutas eliminadas sin `retirada`.

## Fuera de alcance

- El contrato de los endpoints que la página consume: `rutas-de-api`.
- Evaluar la usabilidad: `evaluaciones-de-usabilidad`.
- Revisar la consistencia visual con los tokens y componentes compartidos: `componentes-de-interfaz`.
- Revisar la accesibilidad: `pautas-de-accesibilidad`.
- Diseñar y construir páginas de aterrizaje: `paginas-de-aterrizaje-bento`.
- Encontrar de forma automática páginas del código sin ficha: `verificaciones-vivas`.
- Capas internas del módulo de cliente: `arquitectura-monolitica-por-capas`.

## Cuándo usarlo

- Al crear, mover o eliminar una página, layout, modal con ruta o manejador de ruta del framework.
- Al cambiar el acceso, los datos o los estados de una página.
- Antes de tocar una página existente, para saber qué no hay que romper.

## Cuándo no usarlo

- En aplicaciones sin enrutado (una sola pantalla o widgets embebidos).
- Para documentar componentes sueltos que no son una ruta.

## Entradas y salidas

- Entradas: el código de la página (enrutador, guardas, carga de datos, componentes), el pedido y los ajustes `campos_obligatorios` y `clave_unica`.
- Salidas: fichas `PAG-…` en `uxyngraphar/trabajo/paginas-de-interfaz/<modulo>/` y el informe de `verificar-paginas.py`.

## Paquetes complementarios

- `rutas-de-api`: la tabla «Datos» cita los endpoints y sus fichas.
- `evaluaciones-de-usabilidad`: evalúa lo que la ficha describe.
- `componentes-de-interfaz`: comprueba que los componentes de la página cubran los estados que la ficha decide.
- `verificaciones-vivas`: lista las páginas del código que aún no tienen ficha.
- `contratos-entre-repositorios`: un manejador propio del cliente (BFF) lleva su contrato allí y su ficha aquí.
