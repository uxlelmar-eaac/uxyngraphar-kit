# Cambios

## 1.0.0

- Primera versión: nace de dividir `reglas-del-proyecto` 1.1.0, que mezclaba las reglas del código con la adaptación de paquetes. Se lleva los problemas `paquetes-sin-adaptar-al-proyecto` y `ajustes-locales-desfasados`, la ficha `ajuste` (prefijo `AJL`, carpeta `ajustes-locales`, mismos status y campos), la frase de activación «ajustes locales» y el campo `al_activar_paquete`.
- Los comandos pasan a `scripts/adaptaciones.py`: `ajustes <id-paquete>` (misma salida) y `aprobar-ajuste <AJL-…> --humano`. Verificación propia en `scripts/verificar-adaptaciones.py`.
- Trabajo en `uxyngraphar/trabajo/adaptaciones-de-paquetes/ajustes-locales/` (antes en `uxyngraphar/trabajo/reglas-del-proyecto/ajustes-locales/`; moverlo lo hace el motor con respaldo).
- Proceso en cuatro fases (`consultar-ajustes`, `seguir-ajustes`, `proponer-ajuste`, `verificar`), skills `aplicar-ajustes-locales` y `proponer-ajuste-local` (traídas de `reglas-del-proyecto`) y `revisar-ajustes-desfasados` (nueva), límites, componentes, herramientas, ejemplo y pruebas propias.
- El recordatorio de reglas activas al activar un paquete se conserva leyendo la carpeta de trabajo de `reglas-del-proyecto` solo si ese paquete está instalado.
