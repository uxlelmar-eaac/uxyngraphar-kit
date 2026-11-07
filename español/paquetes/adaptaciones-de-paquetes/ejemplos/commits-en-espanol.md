# Caso: commits en español en un proyecto con `mensajes-de-commit`

## Pedido

«En este proyecto los mensajes de commit van en español; `mensajes-de-commit` nos pide inglés en `preparar-commit`. No quiero editar el paquete.» Proyecto con `mensajes-de-commit` 1.0.0 instalado y sin ajustes previos.

## Recorrido

**consultar-ajustes.** `adaptaciones.py ajustes mensajes-de-commit` → `mensajes-de-commit: 0 ajustes locales activos`. El pedido es crear un ajuste: se salta a `proponer-ajuste`.

**proponer-ajuste-local** (skill). El archivo existe: `uxyngraphar/paquetes/mensajes-de-commit/proceso/preparar-commit.md`.

```
python3 $P/scripts/comun/fichas.py nueva ajuste --slug commits-en-espanol
```

Frontmatter rellenado:

```yaml
paquete: mensajes-de-commit
aplica_a: proceso/preparar-commit.md
huella: null
evo: null
```

En «Qué cambia»: «El mensaje de commit se escribe en español (Conventional Commits, tipo en inglés: `feat: añade cupones al checkout`). El resto de la fase sigue igual.» En «Cuándo retirarlo»: «Cuando `mensajes-de-commit` admita el idioma del commit como ajuste.» `verificar-adaptaciones.py` → `adaptaciones-de-paquetes: 0 errores, 0 avisos`.

La persona lo activa:

```
UXYNGRAPHAR_HUMANO=1 python3 $P/scripts/adaptaciones.py aprobar-ajuste AJL-20261106-commits-en-espanol --humano
/…/app/uxyngraphar/trabajo/adaptaciones-de-paquetes/ajustes-locales/AJL-20261106-commits-en-espanol.md
```

La ficha pasa a `activo` y su `huella` guarda el sha256 de `preparar-commit.md`.

**consultar-ajustes** (en el siguiente pedido que activa `mensajes-de-commit`):

```
python3 $P/scripts/adaptaciones.py ajustes mensajes-de-commit
## AJL-20261106-commits-en-espanol → manda sobre mensajes-de-commit/proceso/preparar-commit.md
…
mensajes-de-commit: 1 ajustes locales activos
```

**seguir-ajustes.** En `preparar-commit`, el agente redacta `feat: añade cupones al checkout` en lugar del mensaje en inglés.

**verificar** (meses después, tras actualizar `mensajes-de-commit`, que cambió `preparar-commit.md`):

```
python3 $P/scripts/verificar-adaptaciones.py
aviso: AJL-20261106-commits-en-espanol: mensajes-de-commit/proceso/preparar-commit.md cambió desde que se aprobó; una persona lo revisa (adaptaciones.py aprobar-ajuste AJL-20261106-commits-en-espanol --humano) o lo retira
adaptaciones-de-paquetes: 0 errores, 1 avisos
```

**revisar-ajustes-desfasados** (skill). El cambio del paquete solo añadía un paso sobre la rama; el idioma sigue en inglés. El agente propone revisarlo y la persona ejecuta `aprobar-ajuste … --humano`, que guarda la huella nueva.

## Resultado

- El paquete instalado sigue íntegro; el idioma de los commits se adapta solo en este proyecto.
- Al actualizar el paquete, el ajuste quedó «por revisar» y nadie lo siguió a ciegas sin saberlo.
- El agente no activó ni revisó nada: propuso y la persona decidió.
