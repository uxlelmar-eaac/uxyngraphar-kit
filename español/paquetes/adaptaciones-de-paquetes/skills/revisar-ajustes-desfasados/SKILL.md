---
name: revisar-ajustes-desfasados
description: Compara un ajuste local por revisar con el archivo actual de su paquete y propone a la persona revisarlo (nueva huella) o retirarlo porque el paquete ya incorporó el cambio.
resuelve: [ajustes-locales-desfasados]
---

# Revisar ajustes desfasados

## Cuándo usarla

- `adaptaciones.py ajustes <id>` marcó un ajuste con `POR REVISAR`.
- `verificar-adaptaciones.py` avisa de que un archivo «cambió desde que se aprobó» o «no está instalado».
- Después de actualizar paquetes, cuando la persona pide repasar los ajustes.

## Pasos

1. Lista los avisos: `python3 $P/scripts/verificar-adaptaciones.py`.
2. Para cada ajuste, lee su «Qué cambia» y el archivo actual `uxyngraphar/paquetes/<paquete>/<aplica_a>` (y el `CHANGELOG.md` del paquete, si lo tiene).
3. Clasifícalo y díselo a la persona con el comando que le toca:
   - El paquete ya hace lo que pedía el ajuste → retirarlo: `python3 $P/scripts/comun/fichas.py estado AJL-… retirado --humano`.
   - Sigue haciendo falta y no choca con el texto nuevo → revisarlo: `python3 $P/scripts/adaptaciones.py aprobar-ajuste AJL-… --humano` (guarda la huella nueva).
   - Sigue haciendo falta pero el texto nuevo cambia lo que sustituye → propón un ajuste nuevo con `proponer-ajuste-local` y que la persona retire el anterior.
   - «Sin paquete» (el paquete o el archivo ya no existen) → retirarlo, o apuntar un ajuste nuevo al archivo que lo sustituye.
4. No edites la ficha activa ni cambies su status: lo decide la persona.

## Resultado

- Cada ajuste desfasado tiene una propuesta concreta (retirar, revisar o reemplazar) y la persona sabe qué comando ejecutar.
