# Calidad de código

Mantiene el código legible para personas y agentes: archivos cortos con una sola responsabilidad y nombres que se explican solos. El tamaño y los nombres de archivo con espacios se comprueban sin IA con `calidad.py`.

## Qué resuelve

Los archivos crecen de cien en cien líneas hasta que nadie los abarca, y los nombres genéricos obligan a leer el cuerpo de cada función para saber qué hace. Este paquete fija un límite de líneas con una forma concreta de dividir (archivos hermanos con nombre relacional y el original como fachada) y un criterio de nombres por tipo de identificador, con el casing de cada lenguaje.

## Problemas que cubre

- `archivos-demasiado-largos`: archivos que pasan de `limite_lineas` y mezclan responsabilidades.
- `nombres-poco-explicativos`: identificadores y archivos genéricos (`data`, `utils.ts`, `handle()`) o con espacios en el nombre.

## Fuera de alcance

- Idioma del código y de los nombres de archivo, glosario de términos de dominio y texto para el usuario por i18n: `idiomas-del-codigo`.
- Formato de los mensajes de commit y de los nombres de rama: `mensajes-de-commit`.
- Reglas propias del equipo comprobables con expresiones regulares: `reglas-del-proyecto`.
- Qué capa o módulo puede importar a cuál: `arquitectura-monolitica-por-capas`.
- Credenciales o archivos de secretos en el código: `secretos-y-credenciales`.
- Formato automático y linters del lenguaje: no lo cubre el kit; es cosa de las herramientas del proyecto.

## Cuándo usarlo

- En cualquier tarea que escriba o modifique código del proyecto.
- Al adoptar el paquete en un proyecto existente (diagnóstico con `calidad.py` sobre todas las `raices`).

## Cuándo no usarlo

- En archivos generados, vendorizados o migraciones ya aplicadas (van en `excluir`).
- Para decidir en qué idioma va un nombre: eso lo fija `idiomas-del-codigo`.

## Entradas y salidas

- Entradas: el código bajo `raices` y los ajustes en `uxyngraphar/trabajo/calidad-de-codigo/ajustes.json`.
- Salidas: código dividido y nombrado según los límites y el informe de `calidad.py` (`archivo: motivo` y un resumen con el número de problemas).

## Paquetes complementarios

- `idiomas-del-codigo`: el idioma de los nombres que este paquete pide que sean explicativos. Si está instalado, sus términos permitidos están en `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md`.
- `mensajes-de-commit`: el mensaje con el que se entrega el cambio.
- `reglas-del-proyecto`: convenciones del equipo que este paquete no fija (prohibir `console.log`, exigir cabeceras).
- `documentacion-espejo`: la ficha de cada archivo nuevo que nace al dividir.
- `deuda-y-mejoras`: la cola donde se registran los archivos que ya excedían el límite y no se tocaron.
