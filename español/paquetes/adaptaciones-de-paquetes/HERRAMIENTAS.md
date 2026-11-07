# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/adaptaciones-de-paquetes`.

## `scripts/adaptaciones.py`

- `python3 $P/scripts/adaptaciones.py ajustes <id-paquete>`: ajustes locales activos de ese paquete, cada uno como `## AJL-… → manda sobre <id>/<archivo>` y su cuerpo, marcando los «por revisar». Termina con `<id>: N ajustes locales activos` y, si `reglas-del-proyecto` está instalado y tiene reglas activas, «· M reglas del proyecto activas: antes de tocar código, `reglas.py para <rutas>`». Es el comando de `al_activar_paquete`.
- `python3 $P/scripts/adaptaciones.py aprobar-ajuste <AJL-…> --humano`: activa o revisa un ajuste y guarda la huella del archivo que complementa. Solo una persona (terminal interactiva o `UXYNGRAPHAR_HUMANO=1`).

## `scripts/verificar-adaptaciones.py`

Verificación del paquete (está en «verificaciones»). Error: un ajuste activo sin `paquete`. Avisos: ajustes activos «por revisar», ajustes no retirados cuyo paquete o archivo no está instalado y ajustes propuestos sin `paquete`. Termina con `adaptaciones-de-paquetes: N errores, M avisos`.

## `scripts/adaptaciones_datos.py`

Librería compartida por los dos anteriores: lectura de las fichas de ajuste, archivo objetivo, huella y estado de cada ajuste, y recuento de las reglas activas de `reglas-del-proyecto` (leyendo su carpeta de trabajo, sin importar nada de ese paquete). No se ejecuta directamente.

## `scripts/comun/fichas.py`

Crea fichas y cambia su status: `nueva ajuste --slug <slug>`, `listar`, `ver <id>`, `estado <id> retirado --humano`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
