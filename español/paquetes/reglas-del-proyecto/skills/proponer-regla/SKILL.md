---
name: proponer-regla
description: Escribe una regla del proyecto en estado propuesta, con nivel, globs de aplica_a, resumen de una línea y, si se puede, una regex prohibida u obligatoria que la compruebe sin IA.
resuelve: [convenciones-sin-comprobar]
---

# Proponer regla

## Cuándo usarla

- La persona pide fijar una convención de su código («nada de `console.log` en `src/`»).
- Una revisión repite el mismo comentario y conviene que lo compruebe un script.

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva regla --slug <slug> --titulo "<título>"`. Nace `propuesta` en `uxyngraphar/trabajo/reglas-del-proyecto/reglas/`.
2. Rellena el frontmatter:
   - `nivel`: `bloqueante` (falla la verificación) o `aviso`.
   - `aplica_a`: lista de globs relativos a la raíz de la app (`src/**/*.ts`).
   - `resumen`: una línea que se pueda cumplir sin leer más.
   - `comprobacion_prohibido`: regex que no debe aparecer en ninguna línea; `comprobacion_obligatorio`: regex que debe aparecer en cada archivo. Vacías = regla sin comprobación (vale como instrucción).
   - `reemplaza`: el id de la regla activa que sustituye, o `null`.
3. Escribe la regex con una sola barra invertida aunque vaya entre comillas (`"console\.log\("`): el frontmatter no interpreta escapes y `\\` llega tal cual a la regex. No uses « #» (espacio + almohadilla): se toma como comentario.
4. Rellena el cuerpo: regla (1–2 frases), porqué (1 frase) y ejemplo `correcto` en vez de `incorrecto`.
5. Ejecuta `python3 $P/scripts/verificar-reglas.py`: si la regex no compila sale un aviso con el error.
6. Mide el impacto antes de que la persona la active: `python3 $P/scripts/reglas.py comprobar` no la evalúa hasta que esté `activa`, así que busca el patrón con `rg '<regex>' <globs>` y da la cifra.

## Resultado

- Una ficha `REG-…` en `propuesta` y el comando que la activa: `fichas.py estado REG-… activa --humano`.
