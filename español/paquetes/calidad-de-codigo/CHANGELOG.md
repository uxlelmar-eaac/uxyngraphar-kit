# Cambios

## 2.0.0

- División del paquete generalista en tres paquetes especializados. `calidad-de-codigo` se queda con `archivos-demasiado-largos` y `nombres-poco-explicativos`; pierde dos problemas del alcance:
  - `codigo-en-idioma-mezclado` pasa a `idiomas-del-codigo` con `scripts/glosario.py`, `plantillas/GLOSARIO.md`, `referencia/idioma.md` y la skill `consultar-glosario`. El glosario del proyecto pasa de `trabajo/calidad-de-codigo/GLOSARIO.md` a `trabajo/idiomas-del-codigo/GLOSARIO.md` (sigue en «protegidos», ahora de ese paquete).
  - `commits-sin-convencion` pasa a `mensajes-de-commit` con la fase `preparar-commit`, la skill `redactar-commit` y la revisión de commits (`calidad.py --commits [N]` → `mensajes-de-commit/scripts/commits.py [N]`; el ajuste `commits_revisar` se va con ella).
- `calidad.py` solo revisa el límite de líneas y los nombres de archivo con espacios; el aviso de nombre no ASCII pasa a `idiomas-del-codigo/scripts/idiomas.py`. Se quitan la opción `--commits`, el campo «protegidos» y la pieza `plantillas`.
- Los ajustes `raices`, `extensiones`, `excluir`, `limite_lineas` y `exenciones_lineas` no cambian.
- `LIMITES.md` pasa de seis a cuatro límites (salen idioma y commits); la tabla «Formato por lenguaje» pasa de `referencia/idioma.md` a `referencia/nombres.md`; el proceso queda en `diagnosticar`, `escribir-codigo` y `verificar`.
- Nueva frase de activación: «nombres autoexplicativos».

## 1.1.0

- Reconstruido con el protocolo de piezas: `PAQUETE.md` (alcance y lo que deja fuera), `LIMITES.md`, proceso en cuatro fases (`diagnosticar`, `escribir-codigo`, `verificar`, `preparar-commit`), cinco skills, `HERRAMIENTAS.md`, ejemplo resuelto y pruebas propias.
- Las reglas del README pasan a `LIMITES.md`, con un límite nuevo: solo se divide lo que el agente hizo crecer.
- `docs/` pasa a `referencia/` (`idioma.md`, `limite-lineas.md`, `nombres.md`); el mensaje de `calidad.py` y la plantilla `GLOSARIO.md` citan la nueva ruta.

## 1.0.0

- Primera versión del paquete en uxyngraphar 2.0.
