---
name: redactar-prohibicion-comprobable
description: Convierte lo que una ADR veta en el código en una expresión regular (comprobacion_prohibido) y los archivos donde aplica (aplica_a), para que verificaciones-vivas lo busque.
resuelve: [prohibiciones-no-comprobables]
---

# Redactar prohibición comprobable

## Cuándo usarla

- En `redactar-adr`, cuando la decisión prohíbe algo que deja rastro en el texto del código: una librería (`axios`, `moment`), una API (`eval(`, `innerHTML =`), un patrón (consultas SQL concatenadas en `src/modules/**`).
- No sirve para prohibiciones de diseño que no se ven en el texto («no acoplar módulos»): esas se quedan en «Consecuencias».

## Pasos

1. Escribe la forma exacta en que aparecería lo prohibido: `import axios from 'axios'`, `require("axios")`.
2. Redacta una expresión regular (sintaxis de Python `re`) que la encuentre sin falsos positivos evidentes: `from .axios.` cubre las comillas simples y dobles del import.
3. Ponla entre comillas en el frontmatter: `comprobacion_prohibido: "from .axios."`.
4. Acota los archivos con globs relativos a la raíz de la app: `aplica_a: [src/**/*.ts]`. Sin `aplica_a`, se busca en todo el código que revise `verificaciones-vivas`.
5. Comprueba la expresión antes de proponer la ADR: `python3 -c "import re; re.compile(r'from .axios.')"` no debe fallar y, si el proyecto ya cumple la decisión, una búsqueda en `src/` no debe dar resultados (o los resultados son lo que la ADR quiere eliminar: dilo en «Consecuencias»).

## Resultado

- `comprobacion_prohibido` y `aplica_a` rellenos y probados; una vez aceptada la ADR, `verificaciones-vivas` informa de cada aparición como hallazgo de severidad alta.
