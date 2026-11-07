# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/idiomas-del-codigo`.

## `scripts/idiomas.py`

Verificación del paquete (está en «verificaciones»).

- `python3 $P/scripts/idiomas.py`: revisa todos los archivos de `raices` con alguna de las `extensiones` y fuera de `excluir`.
- `python3 $P/scripts/idiomas.py <archivo>…`: revisa solo esos archivos (los que no tienen una extensión de código o están excluidos se ignoran).

Qué detecta: nombres de archivo (o de alguna carpeta de su ruta) con caracteres no ASCII. Imprime una línea por problema y un resumen; código 0 = sin problemas, 1 = hay problemas. El idioma de los identificadores y comentarios no se comprueba con el script: lo revisa el agente con `referencia/idioma.md` y el glosario.

## `scripts/glosario.py`

- `python3 $P/scripts/glosario.py terminos`: términos del dominio permitidos sin traducir (primera columna de la tabla de `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md`).
- `python3 $P/scripts/glosario.py iniciar`: crea `GLOSARIO.md` en el trabajo del paquete desde `plantillas/GLOSARIO.md` si falta e imprime su ruta. El archivo está en «protegidos»: lo rellena una persona.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
