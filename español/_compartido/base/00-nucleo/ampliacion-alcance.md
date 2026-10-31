# Ampliación del alcance de archivos de código (R-21)

> Regla dura. Aplica a toda instrucción que toque código. Fuente única en el tooling: `scripts/decisiones/alcance.py`.

**Estándar:** cada instrucción toca como máximo **5 archivos de código** (`presupuesto_max_archivos_codigo: 5`, R-06). Varios rangos del mismo archivo cuentan como uno.

Cuando el pedido necesita más (p. ej. pasar de 5 a 7 archivos para cubrir dos módulos nuevos), el agente **no edita nada** hasta resolver la situación por uno de estos dos frentes. Los dos son obligatorios en el sentido de que no hay una tercera vía: o se fracciona o se pide la ampliación.

## Paso 0 — Evaluar la necesidad crítica

Antes de elegir frente, el agente responde por escrito en la sección `## Alcance → Archivos de código` de la ficha:

> ¿Existe un subconjunto de ≤5 archivos que se pueda **entregar solo**, compilando, con las pruebas en verde y **sin romper contratos** (API, esquema de datos, IDs compartidos, tipos públicos)?

| Respuesta | Conclusión | Frente |
|-----------|------------|--------|
| **Sí existe** | La ampliación **no** es sumamente necesaria | **B — Fraccionar** |
| **No existe** | La ampliación **sí** es sumamente necesaria | **A — Ampliar con aprobación** |

La justificación tiene que ser concreta: nombrar qué se rompería y entre qué archivos. «Es más cómodo», «ahorra una instrucción» o «son archivos pequeños» **no** justifican una ampliación.

### Señales de que NO es sumamente necesaria (→ fraccionar)

- Son **módulos independientes** entre sí (el caso típico de «dos módulos nuevos»): cada uno compila y se prueba solo.
- Lo que sobra son pruebas, documentación de código, estilos o configuración que pueden ir en una entrega posterior.
- Hay un refactor «aprovechando que estoy aquí» (eso es deuda fuera de alcance → ficha en `45`, R-09).
- El orden natural es secuencial: primero el módulo base, después quien lo consume.

### Señales de que SÍ es sumamente necesaria (→ ampliar)

- Un **cambio de contrato** (firma pública, esquema, payload) obliga a tocar a la vez productor y consumidores; a medias no compila o rompe en ejecución.
- Una **migración atómica** (renombrar un ID compartido, mover un tipo) que deja el sistema roto entre entregas.
- Un cambio de seguridad que sería peligroso desplegar a medias.

## Frente A — Ampliación con aprobación humana (necesidad crítica)

1. Declarar en el frontmatter:
   - `ampliacion_factor`: entre **1.5 y 2** (nunca más de 2×). Tope de archivos = `floor(5 × factor)`:

     | Factor | Tope |
     |--------|------|
     | 1.5 | 7 |
     | 1.6–1.7 | 8 |
     | 1.8–1.9 | 9 |
     | 2 | 10 |

   - `ampliacion_justificacion`: una frase con **qué se rompe** si se entrega en partes de ≤5.
   - `presupuesto_max_archivos_codigo`: el número real de archivos (≤ tope).
2. En `## Alcance`, listar **cada archivo extra** (del 6.º en adelante) con su motivo.
3. Dejar la instrucción en `awaiting_approval` y **esperar la aprobación humana explícita antes de proceder**. Aprobar la instrucción (`decisiones.py apply`) fija `ampliacion_aprobada_at`; sin ese campo:
   - `contexto.py` sale con código 3 y **no entrega código**;
   - el validador marca error R-21 en `02-en-progreso/`;
   - `controlar.py` avisa o bloquea si el cambio supera el tope permitido;
   - `decisiones.py cerrar` no cierra la instrucción.
4. Si ni con 2× alcanza → se fracciona igualmente, en bloques de ≤10, cada uno con su propia ampliación aprobada.

Usar el factor **mínimo** que cubra la necesidad: si bastan 7 archivos, `1.5`, no `2`.

## Frente B — Fraccionamiento (sin necesidad crítica)

1. La instrucción original pasa a ser el **plan**: describe el objetivo completo y lista sus fracciones, pero no toca código.
2. Crear una instrucción hija por entrega, cada una con **≤5 archivos de código** (el estándar, sin exceder):
   - `fraccion_de: <id del plan>`
   - `depende_de: [<ids de fracciones que deben cerrarse antes>]` (vacío si es independiente)
3. Cada fracción es una **entrega parcial completa**: compila, pasa pruebas, actualiza su espejo y se cierra sola.
4. Las fracciones se aprueban y ejecutan por separado, en el orden que marquen las dependencias.

### Ejemplo: 7 archivos para dos módulos nuevos independientes

```yaml
# 20261028-001-modulos-pagos-y-avisos  (plan; no toca código)
presupuesto_max_archivos_codigo: 0

# 20261028-002-modulo-pagos
fraccion_de: 20261028-001-modulos-pagos-y-avisos
anclas_codigo: [src/pagos/servicio.ts, src/pagos/rutas.ts, src/pagos/pagos.test.ts, src/app.ts]   # 4

# 20261028-003-modulo-avisos
fraccion_de: 20261028-001-modulos-pagos-y-avisos
depende_de: [20261028-002-modulo-pagos]   # registra sus rutas en src/app.ts después de pagos
anclas_codigo: [src/avisos/servicio.ts, src/avisos/rutas.ts, src/app.ts]                            # 3
```

Justificación en `Alcance` del plan: «No es sumamente necesaria: pagos y avisos no comparten contrato; cada módulo compila y se prueba solo. Se fracciona en 002 (4 archivos) y 003 (3 archivos).»

### Ejemplo: 7 archivos por un cambio de contrato

```yaml
anclas_codigo: [api/tipos.ts, api/usuarios.ts, web/cliente.ts, web/perfil.tsx, web/ajustes.tsx, worker/sync.ts, api/usuarios.test.ts]
presupuesto_max_archivos_codigo: 7
ampliacion_factor: 1.5
ampliacion_justificacion: "Renombrar el campo `email` → `correo` en el contrato de usuario: si se entrega solo el API, web y worker dejan de compilar."
```

## Resumen para el agente

1. ¿>5 archivos de código? Para y evalúa (paso 0). Escribe la justificación en `Alcance`.
2. ¿No es sumamente necesaria? → **fracciona** en hijas de ≤5. No pidas ampliación.
3. ¿Sí lo es? → `ampliacion_factor` 1.5–2 + justificación + lista de archivos extra, y **espera aprobación humana** antes de tocar código.
4. Nunca más de 2× (10 archivos) en una sola instrucción.

Relacionado: [eficiencia-ia.md](eficiencia-ia.md) (presupuesto) · [frontmatter/instruccion.md](frontmatter/instruccion.md) (campos) · [../05-instrucciones/_PROTOCOLO.md](../05-instrucciones/_PROTOCOLO.md).
