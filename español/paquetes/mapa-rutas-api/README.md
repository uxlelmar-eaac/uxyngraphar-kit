# Mapa de rutas de API

Activado con «usa el paquete mapa-rutas-api» / «sigue el protocolo endpoints» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/mapa-rutas-api/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Antes de tocar un endpoint, lee su ficha: `python3 $S/comun/fichas.py listar ruta` y `python3 $S/comun/fichas.py ver <id>`.
4. Endpoint nuevo: `python3 $S/comun/fichas.py nueva ruta --slug <metodo-ruta> --en <modulo> --titulo "GET /orders"`.
5. Al cambiar método, ruta, autenticación, entrada, salida o archivos, actualiza la ficha en la misma tarea. Endpoint eliminado: `fichas.py estado <id> retirada`.
6. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-rutas.py`.

Trabajo: `uxyngraphar/trabajo/mapa-rutas-api/<modulo>/`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Una ficha por endpoint** (método + ruta). No hay dos fichas activas con la misma combinación.
2. **Ficha viva:** todo cambio de contrato (ruta, método, autenticación, roles, entrada, salida, errores) actualiza la ficha en la misma tarea.
3. **Contrato antes que implementación:** «Entrada» y «Salida» describen lo que ve el cliente, incluidos códigos de error relevantes.
4. **Archivos ancla reales:** rutas existentes en el repo (controlador, caso de uso, DTO, pruebas).
5. **Seguridad explícita:** `auth` (`public`, `bearer`, `cookie`, `api-key`…) y `roles` siempre declarados; un endpoint público se justifica en «Hace».
6. **Agrupar por módulo:** `--en <modulo>`.
7. **No borrar fichas:** un endpoint eliminado pasa a `retirada`; uno en desuso, a `deprecada` con la alternativa.
