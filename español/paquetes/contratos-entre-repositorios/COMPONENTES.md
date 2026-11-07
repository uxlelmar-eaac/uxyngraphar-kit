# Componentes

Las piezas que define el paquete.

## Id compartido

`id_compartido`: nombre estable del contrato, idéntico en todos los repositorios, con la forma `modulo.recurso.accion` (minúsculas, guiones y al menos un punto: `orders.list`, `orders.item.cancel`). Es la clave con la que `comparar` empareja contratos. No se renombra nunca: renombrar es crear un contrato nuevo y retirar el anterior.

## Contrato

Ficha `CON-…` de un repositorio (plantilla `plantillas/contrato.md`). Frontmatter: `id_compartido`, `rol`, `method`, `path`, `version`, `proveedor`, `ficha_proveedor`, `consumidores`. Secciones: «Para qué se usa», «Forma (resumen)» y «Cambios incompatibles». Status: `propuesto` (inicial), `vigente` y `retirado` (solo una persona) y `deprecado`.

## Rol

Papel del repositorio en el contrato: `proveedor` (sirve la API), `consumidor` (la llama) o `bff` (manejador propio del cliente que hace de intermediario). Un consumidor vigente debe citar `ficha_proveedor`.

## Ficha del proveedor

La ficha de la ruta en `rutas-de-api` del repositorio proveedor, citada por URL o ruta en `ficha_proveedor`. Es la fuente humana del contrato; el consumidor nunca la copia.

## Registro

`uxyngraphar/trabajo/contratos-entre-repositorios/REGISTRO.md`: tabla generada por `contratos.py registro` con cada contrato de este repositorio (id compartido, rol, ruta, versión, proveedor, ficha, estado). No se edita a mano.

## Repositorios hermanos

Los demás repositorios del sistema, listados en `otros_repos` como rutas relativas a la raíz de esta app. Si están al lado y tienen `uxyngraphar/trabajo/`, `comparar` y `verificar-contratos.py` leen sus contratos y sus fichas de `rutas-de-api` (solo lectura).
