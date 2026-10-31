# Sistema integral vs detalle de capa (cliente)

## Regla rápida

| Pregunta | Dónde |
|----------|-------|
| ¿Dónde está la pantalla / componente? | Espejo `50-sistema-integral/src/.../` |
| ¿Implementar o cambiar un módulo UI/BFF? | `25-areas/` + `15-rutas/` (solo BFF) |
| ¿API backend? | Ficha en repo servidor; citar id en `.md` del espejo |
| ¿Investigación puntual? | `40-auditorias/02-en-progreso/` |

## Tres capas

```
50-sistema-integral/src/.../   ← espejo 1:1 del scaffolding UI (solo .md)
25-areas/<id>/                 ← CONTEXTO para IA por dominio
15-rutas/                      ← fichas BFF propias
```

El espejo **no inventa carpetas**: copia las del proyecto (`src/app/`, `src/components/`, etc.). La IA lo genera con la instrucción `_PLANTILLA-generar-espejo-integral.md`.

## IA

- Tarea de código → `lectura_minima` en CONTEXTO/fichas.
- Entender mapa del repo → uno o pocos `README.md` del espejo citados en instrucción.
- Generar espejo → instrucción tipo `generar-espejo-integral`; `presupuesto_max_archivos_codigo: 0`.

Ver [generar-documentacion-integral.md](generar-documentacion-integral.md) y [50-sistema-integral/_PROTOCOLO.md](../50-sistema-integral/_PROTOCOLO.md).
