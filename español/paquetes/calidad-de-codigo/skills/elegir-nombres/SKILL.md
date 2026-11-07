---
name: elegir-nombres
description: Elige nombres para identificadores, archivos y carpetas nuevos que digan qué son, para qué sirven y en qué unidad, con el casing del lenguaje y sin genéricos.
resuelve: [nombres-poco-explicativos]
---

# Elegir nombres

## Cuándo usarla

- Al crear cualquier variable, función, tipo, constante, archivo o carpeta.
- Al revisar un cambio donde aparecen `data`, `tmp`, `obj`, `x`, `flag`, `handle()`, `utils.ts` o números mágicos.

## Pasos

1. Responde sin comentarios: ¿qué es?, ¿para qué sirve?, ¿en qué unidad o dominio? (`requestTimeoutMs`, no `timeout`).
2. Aplica la forma según el tipo de nombre:
   - Funciones: verbo + objeto (`submitPaymentForm`).
   - Booleanos: aserción positiva con `is`/`has`/`can`/`should` (`isEmailVerified`, no `isNotDisabled`).
   - Colecciones en plural, elementos en singular.
   - Constantes de dominio en un objeto o enum con nombre (`ORDER_STATUS.SHIPPED`, no `3`).
   - Archivos por responsabilidad y sin espacios (`date-formatting.ts`, no `utils.ts` ni `date formatting.ts`).
3. Usa el casing del lenguaje (tabla «Formato por lenguaje» de `referencia/nombres.md`).
4. Abreviaturas solo universales (`id`, `url`, `http`).
5. El idioma del nombre no lo decide este paquete: si está instalado `idiomas-del-codigo`, síguelo (sus términos permitidos están en `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md`); si no, usa el idioma del código que rodea al cambio.

## Resultado

- Nombres nuevos que se entienden sin leer el cuerpo y que cumplen el límite 2 de `LIMITES.md`.
