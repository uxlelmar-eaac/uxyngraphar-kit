---
name: anotar-fuera-de-alcance
description: Anota en la instrucción en curso la deuda, los bugs o las mejoras detectadas que no forman parte del cambio aprobado, sin implementarlos.
resuelve: [alcance-desbordado]
---

# Anotar fuera de alcance

## Cuándo usarla

- Durante `implementar` o `cargar-contexto`, al ver algo mejorable o roto fuera de lo que la instrucción pide.
- Cuando la persona pide en el chat «ya que estás, arregla también…» algo que no está en las anclas.

## Pasos

1. Escribe una viñeta en la sección «Fuera de alcance» de la instrucción: qué es, dónde (`ruta:línea`) y por qué importa, en una línea.
2. No lo arregles, aunque sea una línea: entra en otra instrucción o, si está instalado `deuda-y-mejoras`, en su cola.
3. Si la persona lo pidió en el chat, respóndele que queda anotado y que necesita su propia instrucción (o una ampliación aprobada de esta).
4. Al cerrar, menciona estas viñetas en el resumen para la persona.

## Resultado

- La sección «Fuera de alcance» de la instrucción recoge todo lo detectado y no hecho, con su ubicación.
