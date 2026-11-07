---
name: buscar-adr-vigentes
description: Encuentra las ADR aceptadas (y las abiertas) que tratan un tema antes de decidir o cambiar algo estructural.
resuelve: [decisiones-contradichas, decisiones-sin-registro]
---

# Buscar ADR vigentes

## Cuándo usarla

- En `consultar-vigentes`, siempre.
- Cuando otro paquete o una instrucción va a tocar algo estructural (dependencias, base de datos, autenticación, comunicación entre servicios) y hay que saber si una ADR lo condiciona.

## Pasos

1. Lista las vigentes: `python3 $P/scripts/comun/fichas.py listar adr --status aceptada`. Cada línea es `id	status	título`.
2. Lista las abiertas del mismo tema: `fichas.py listar adr --status propuesta` y `--status en-evaluacion`.
3. Si el título no basta, busca los términos del pedido dentro de las ADR aceptadas (están en `uxyngraphar/trabajo/decisiones-de-arquitectura/completadas/`): nombre de la tecnología, del área o de la librería.
4. Abre solo las que coinciden (`fichas.py ver <id>`) y lee «Decisión» y «Consecuencias».
5. Clasifica cada una: el pedido la cumple, la contradice o no le afecta.

## Resultado

- Lista de ADR que condicionan el pedido, cada una con «cumple», «contradice» o «no afecta», y las abiertas sobre el mismo tema.
