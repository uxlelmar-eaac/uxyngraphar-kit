# Componentes

Las piezas que define el paquete. El trabajo vive en `uxyngraphar/trabajo/decisiones-de-arquitectura/<carpeta-de-estado>/`.

## ADR

Ficha `ADR-<AAAAMMDD>-<slug>` (registro de decisión de arquitectura): una decisión técnica cara de revertir con su contexto, las opciones consideradas, la decisión, sus consecuencias y su seguimiento.

## Estados de una ADR

| Status | Carpeta | Quién lo pone | Significado |
|--------|---------|---------------|-------------|
| `propuesta` | `pendientes` | al crearla | borrador del agente o de la persona |
| `en-evaluacion` | `en-progreso` | el agente, cuando está lista | espera la decisión de la persona |
| `aceptada` | `completadas` | solo una persona (`--humano`) | vinculante para todo el trabajo |
| `rechazada` | `canceladas` | solo una persona (`--humano`) | descartada; queda como registro |
| `reemplazada` | `archivadas` | tras aceptarse la que la sustituye | ya no vale; ver `reemplazada_por` |
| `obsoleta` | `archivadas` | cuando deja de aplicar sin sustituta | ya no vale |
| `para-eliminar` | `para-eliminar` | — | creada por error |

`propuesta` y `en-evaluacion` esperan a una persona: `revision-humana` las recoge.

## Reemplazo

Par de campos que enlaza dos ADR: la nueva lleva `reemplaza: <id>`; la anterior, al archivarse, `reemplazada_por: <id>`. Es la única forma de cambiar una decisión aceptada.

## Prohibición comprobable

`comprobacion_prohibido`: expresión regular de lo que la decisión veta en el código; `aplica_a`: globs de los archivos donde se busca. Solo cuentan en ADR `aceptada`; las busca `verificaciones-vivas`.

## Áreas

`areas`: lista de áreas funcionales o técnicas que la decisión afecta (las de `mapa-de-modulos`, si está instalado). Sirve para encontrar las ADR de un área.
