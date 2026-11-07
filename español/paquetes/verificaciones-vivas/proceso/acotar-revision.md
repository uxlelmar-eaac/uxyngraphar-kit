---
fase: acotar-revision
resuelve: []
skills: []
---

# Fase: acotar revisión

## Objetivo

Elegir qué revisiones tienen sentido para el pedido y para los paquetes instalados, y confirmar que los ajustes no van a producir ruido.

## Entradas

- El pedido de la persona («revisa las rutas», «¿está al día la documentación?», «comprueba que arranca»).
- Los paquetes instalados en `uxyngraphar/paquetes/`.
- Los ajustes efectivos (`prefijo_global`, `excluir`, `humo`, `dias_manual`).

## Pasos

1. Traduce el pedido a revisiones (tabla de `COMPONENTES.md`): rutas y páginas → `rutas`, `paginas`; documentación en general → todas menos `humo`; arranque → `humo`.
2. Descarta las que necesitan un paquete que no está instalado (devolverían solo una nota `info`).
3. Si el servidor añade un prefijo global a las rutas y `prefijo_global` está vacío, avisa a la persona antes de ejecutar `rutas`: todas saldrían como «sin ficha».
4. Si se pide `humo`, lee los comandos de `humo` y confirma que apuntan a un entorno de prueba (límite 3); si no hay comandos, dilo.
5. Pregunta si quiere constancia (`--informe`) cuando el pedido no lo diga.

## Criterio de salida

- Tienes la lista de revisiones a ejecutar, si lleva `--ejecutar` y si lleva `--informe`.
