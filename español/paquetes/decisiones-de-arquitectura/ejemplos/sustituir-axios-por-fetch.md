# Caso: dejar axios y usar fetch, reemplazando una ADR anterior

## Pedido

«Quiero quitar axios del cliente; con `fetch` nativo nos basta.» En el trabajo hay una ADR aceptada, `ADR-20250310-cliente-http-axios`, que eligió axios por sus interceptores.

## Recorrido

**consultar-vigentes.** Skill `buscar-adr-vigentes`:

```
python3 $P/scripts/comun/fichas.py listar adr --status aceptada
ADR-20250310-cliente-http-axios	aceptada	Usar axios como cliente HTTP
ADR-20250402-usar-postgres	aceptada	Usar PostgreSQL como base de datos
```

`ADR-20250310-cliente-http-axios` contradice el pedido. No se toca el código: lo que sigue es una ADR que la reemplace.

**redactar-adr.**

```
python3 $P/scripts/comun/fichas.py nueva adr --slug sin-axios --titulo "Usar fetch nativo en lugar de axios"
uxyngraphar/trabajo/decisiones-de-arquitectura/pendientes/ADR-20261106-sin-axios.md
```

Contenido, resumido:

- Contexto: axios solo se usa en `src/api/client.ts` y en 14 llamadas; el único interceptor añade la cabecera `Authorization`. El navegador y Node 20 traen `fetch`.
- Opciones: (1) seguir con axios: sin trabajo, pero una dependencia y 13 kB más en el paquete del cliente; (2) `fetch` con un envoltorio propio en `src/api/client.ts`: sin dependencia, pero el envoltorio hay que mantenerlo y no hay cancelación por tiempo sin `AbortController`; (3) otra librería (`ky`): menos peso, pero cambia una dependencia por otra.
- Decisión: opción 2, porque el único interceptor cabe en diez líneas.
- Consecuencias negativas: los tiempos de espera se implementan a mano con `AbortController`.
- Frontmatter: `reemplaza: ADR-20250310-cliente-http-axios`, `areas: [api]`.

Skill `redactar-prohibicion-comprobable`:

```yaml
comprobacion_prohibido: "from .axios."
aplica_a: [src/**/*.ts]
```

Comprobada con `re.compile`; hoy da 15 coincidencias en `src/`, que son exactamente lo que la ADR quiere eliminar (anotado en «Consecuencias»).

**someter-a-evaluacion.**

```
python3 $P/scripts/comun/fichas.py estado ADR-20261106-sin-axios en-evaluacion
uxyngraphar/trabajo/decisiones-de-arquitectura/en-progreso/ADR-20261106-sin-axios.md
```

Resumen para la persona: «Propone sustituir axios por `fetch` con un envoltorio propio; coste: tiempos de espera a mano; deja sin efecto `ADR-20250310-cliente-http-axios`». Comandos: `fichas.py estado ADR-20261106-sin-axios aceptada --humano` o `rechazada --humano`. Si el agente intentara aceptarla:

```
python3 $P/scripts/comun/fichas.py estado ADR-20261106-sin-axios aceptada
error: «aceptada» solo lo asigna una persona (usa --humano si eres tú)
```

**registrar-reemplazo.** La persona la acepta. Skill `reemplazar-adr`: en `ADR-20250310-cliente-http-axios` se cambia solo `reemplazada_por: ADR-20261106-sin-axios` y:

```
python3 $P/scripts/comun/fichas.py estado ADR-20250310-cliente-http-axios reemplazada
uxyngraphar/trabajo/decisiones-de-arquitectura/archivadas/ADR-20250310-cliente-http-axios.md
```

## Resultado

- Una ADR aceptada nueva y la anterior archivada con su texto intacto, enlazadas en ambos sentidos.
- `verificaciones-vivas` informará de cada `from 'axios'` hasta que desaparezcan. Quitar axios del código es otro trabajo: una instrucción aprobada que cite la ADR.
