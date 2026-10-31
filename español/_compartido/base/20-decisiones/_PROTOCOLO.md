# Protocolo — decisiones (ADR)

Registro de decisiones arquitectónicas que afectan implementación y documentación. Organización por estados y fechas (R-17):

```
20-decisiones/
├── 01-pendientes/YYYY-MM-DD/   ← propuesta
├── 02-en-progreso/             ← en-evaluacion (uso raro)
├── 03-completadas/YYYY-MM-DD/  ← aceptada
├── 04-archivadas/YYYY-MM-DD/   ← reemplazada, obsoleta
├── 05-canceladas/YYYY-MM-DD/   ← rechazada
└── 06-listas-para-eliminar/    ← para-eliminar
```

Archivo: `ADR-NNN-kebab-slug.md` dentro de la carpeta de fecha de creación; `id: ADR-NNN`.

## Cuándo crear ADR

- Cambio de patrón transversal (auth, errores, integraciones).
- Trade-off con impacto en varios módulos.
- Decisión que la IA debe respetar en instrucciones futuras.

## Flujo

El punto de partida depende de si la decisión **ya está tomada** (R-16):

- **Decisión abierta** → borrador desde [_PLANTILLA-ADR.md](_PLANTILLA-ADR.md) con `status: propuesta` en `01-pendientes/` y bloque **Decisión a tomar**. El efecto **no se implementa** todavía.
- **Decisión ya tomada** por el humano (en la instrucción `approved` o explícitamente en sesión) → el ADR se emite directamente con `status: aceptada` en `03-completadas/`, **sin** bloque de decisión y **con** sección **Aprobación** (quién, cuándo, dónde).

Después, en ambos casos:

1. Enlazar desde `25-areas/<area>/CONTEXTO.md` si aplica.
2. Si se reemplaza: nuevo ADR + marcar anterior `reemplazada` + campo `reemplaza` + moverla a `04-archivadas/`.

Nunca se publica un ADR `propuesta` cuyo efecto ya esté en el código: ver R-16.

## Promoción desde auditoría

Hallazgo en `40-auditorias/02-en-progreso/` que cambia reglas → promover a ADR (ver plantilla auditoría `promociones`).

## Convenciones

- Id: `ADR-NNN` en frontmatter; archivo `ADR-NNN-kebab-slug.md` en `<estado>/YYYY-MM-DD/`.
- Frontmatter: [convenciones-frontmatter.md](../00-nucleo/convenciones-frontmatter.md).
- ADRs se citan por `id` (`ADR-NNN`); la ruta cambia con el estado.
