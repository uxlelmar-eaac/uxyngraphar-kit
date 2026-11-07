---
fase: verificar
resuelve: [rutas-de-interfaz-documentadas-dos-veces, fichas-de-pagina-desfasadas]
skills: []
---

# Fase: verificar

## Objetivo

Demostrar que las fichas tienen los campos obligatorios, que ninguna ruta está documentada dos veces y que las anclas existen.

## Entradas

- Las fichas creadas o tocadas en `documentar-cambio`.

## Pasos

1. Ejecuta `python3 $P/scripts/verificar-paginas.py`.
2. Cada `error:` se corrige ahora: `faltan campos …` → rellena el frontmatter; `«/checkout» ya está documentada en …` → une las fichas o pasa la vieja a `retirada`.
3. Cada `aviso: … archivo ancla inexistente …` de una ficha que tocaste se corrige; los de fichas ajenas al pedido se mencionan al cerrar.
4. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- `verificar-paginas.py` termina con código 0 y sin avisos en las fichas tocadas.
- `verificar.py` sin errores.
