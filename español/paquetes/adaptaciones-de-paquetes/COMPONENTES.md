# Componentes

Las piezas que define el paquete. Las fichas viven en `uxyngraphar/trabajo/adaptaciones-de-paquetes/ajustes-locales/`.

## Ajuste local

Ficha `AJL-…` en `ajustes-locales/` (plantilla `plantillas/ajuste.md`). Lo que, solo en este proyecto, manda sobre un archivo (`aplica_a`, relativo a la carpeta del paquete) de otro paquete instalado (`paquete`), sin editarlo. Campos: `paquete`, `aplica_a`, `huella`, `evo` (EVO que lo origina, si existe) y `aprobado_por`. Status: `propuesto`, `activo` (se pone con `adaptaciones.py aprobar-ajuste … --humano`) y `retirado`; los dos últimos solo los pone una persona.

## Huella

El sha256 del archivo del paquete al que apunta un ajuste, guardado al aprobarlo. Si el archivo cambia (el paquete se actualizó), el ajuste pasa a «por revisar».

## Estado del ajuste

Lo calcula el script a partir de la huella, sin guardarlo en la ficha: `vigente` (el archivo no cambió), `por revisar` (cambió: se sigue aplicando, pero una persona debe revisarlo con `aprobar-ajuste` o retirarlo) o `sin paquete` (el paquete o el archivo ya no está instalado: no hay nada que sustituir).

## Activación

El campo `al_activar_paquete` del manifiesto (`scripts/adaptaciones.py ajustes {id}`) hace que el agente imprima los ajustes activos de cada paquete que activa, con este paquete nombrado o no.
