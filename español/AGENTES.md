# Agentes en el kit uxyngraphar

Esta carpeta es el kit: el motor (`motor/`) y el catálogo de sistemas (`sistemas-de-gobernanza/`). No es un proyecto con sistemas instalados.

- **Crear un sistema:** sigue [`motor/GUIA-PARA-AGENTES.md`](motor/GUIA-PARA-AGENTES.md) y usa siempre el generador
  (`python3 motor/uxyngraphar.py generar …` o `crear`); nunca copies `sistemas-de-gobernanza/_base/` ni otro sistema a mano.
- **Cambiar un sistema:** edita solo `sistemas-de-gobernanza/<id>/`; tras tocar `sistema.json`, `python3 motor/uxyngraphar.py indice-sistema <id>`.
  Cierra con `python3 motor/uxyngraphar.py generar pendientes <id> --json` en «listo», su `CHANGELOG.md` y su versión.
- **Al empezar:** `python3 motor/uxyngraphar.py sincronizar-comun` (copias locales de `scripts/comun/`, que git no versiona).
- **Antes de terminar:** `python3 motor/uxyngraphar.py validar --json` sin errores y, si tocaste el motor,
  `python3 -m unittest discover -s motor/pruebas -t motor/pruebas`.
- **`sistemas-de-gobernanza/_base/`** es el protocolo del que nacen los sistemas, no un sistema: cambiarlo cambia todos los sistemas nuevos.
- Las normas: [`motor/ESPECIFICACION.md`](motor/ESPECIFICACION.md), [`motor/NOMENCLATURA.md`](motor/NOMENCLATURA.md),
  [`motor/GUIA-DE-SISTEMAS.md`](motor/GUIA-DE-SISTEMAS.md) y [`motor/GENERADOR.md`](motor/GENERADOR.md).
