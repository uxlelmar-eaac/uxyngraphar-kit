# Preguntas — índice
<!-- uxyngraphar:inicio -->

Sesiones de clarificación **antes** de crear la instrucción. Organización por **estado** y **fecha de creación** (`YYYY-MM-DD`). El árbol es el índice; no se mantiene tabla manual.

```
03-preguntas/
├── 01-en-curso/YYYY-MM-DD/     ← sesión abierta (chat en curso)
├── 03-completadas/YYYY-MM-DD/  ← rondas cerradas; Q&A volcado a la instrucción
└── 05-canceladas/YYYY-MM-DD/   ← abandonada o saltada sin instrucción
```

- Protocolo: [_PROTOCOLO.md](_PROTOCOLO.md)
- Guía: [fase-preguntas.md](../10-guias/fase-preguntas.md)
- Config: `preguntas` en `uxyngraphar.config.json` (por defecto activo, topes `rondas` `[6, 4, 2]`, `presupuesto_max` 12)

Estados (`status`): `en-curso` (01) · `completada` (03) · `cancelada` (05).

No hay plantilla aparte ni tipo en `decisiones.py`: el agente escribe la ficha (formato de decisión) y, al cerrar, vuelca las **decisiones** a la instrucción (`05-instrucciones/_PLANTILLA.md` § Clarificación).
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
