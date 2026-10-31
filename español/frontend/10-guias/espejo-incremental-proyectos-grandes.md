# Espejo incremental en proyectos medianos y grandes

Estrategia para que **`50-sistema-integral/` crezca con cada instrucción** y una petición futura de «documentación general del sistema» cueste **pocos tokens**.

## Problema

| Tamaño | Enfoque masivo (`_PLANTILLA-generar-espejo-integral`) | Riesgo |
|--------|------------------------------------------------------|--------|
| Pequeño | Una instrucción, espejo completo | Aceptable |
| Mediano / grande / muy grande | Escanear todo el scaffolding de golpe | Muy demandante en tokens, tiempo y revisión humana |

## Solución: dos fases

```mermaid
flowchart LR
  P[Politica incremental aprobada] --> F[Instrucciones normales de producto]
  F --> E[espejo_actualizar en cada cierre]
  E --> R[registro-cobertura-espejo.md]
  R --> C[Consolidar solo huecos]
  C --> M[Mapa integral utilizable]
```

### Fase 1 — Acumulación (día a día)

Cada feature, fix o pantalla UI/BFF usa la plantilla estándar [_PLANTILLA.md](../05-instrucciones/_PLANTILLA.md) (anclas típicas: `src/app/`, componentes, handlers BFF):

1. `anclas_codigo` → qué código toca la tarea.
2. `espejo_actualizar` → qué `.md` del espejo se crea o actualiza **en el mismo cierre**.
3. Al `done`: actualizar [`registro-cobertura-espejo.md`](../50-sistema-integral/registro-cobertura-espejo.md).

La IA **no lee** el espejo entero; solo **escribe** paths declarados ([eficiencia-ia.md](../00-nucleo/eficiencia-ia.md)).

### Fase 2 — Consolidación (cuando el humano pide doc general)

Copiar [_PLANTILLA-consolidar-espejo-integral.md](../05-instrucciones/_PLANTILLA-consolidar-espejo-integral.md):

1. Leer **solo** el registro de cobertura (estado + huecos).
2. Procesar **lista cerrada** `paths_huecos` — no resync masivo.
3. Actualizar registro e índice raíz del espejo si hace falta.

Coste bajo porque la mayoría del mapa **ya existe** gracias a la fase 1.

## Cuándo usar cada plantilla

| Situación | Plantilla |
|-----------|-----------|
| Proyecto mediano+ al adoptar pack | [_PLANTILLA-politica-espejo-incremental.md](../05-instrucciones/_PLANTILLA-politica-espejo-incremental.md) — **una vez** |
| Cada cambio de producto | [_PLANTILLA.md](../05-instrucciones/_PLANTILLA.md) + `espejo_actualizar` |
| «Documentación general» / completar mapa | [_PLANTILLA-consolidar-espejo-integral.md](../05-instrucciones/_PLANTILLA-consolidar-espejo-integral.md) |
| Proyecto pequeño o espejo vacío | [_PLANTILLA-generar-espejo-integral.md](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md) |

## Registro de cobertura

Archivo vivo: [`50-sistema-integral/registro-cobertura-espejo.md`](../50-sistema-integral/registro-cobertura-espejo.md).

| Sección | Uso |
|---------|-----|
| Política incremental | `activa` / `no adoptada` |
| Cobertura por raíz | Resumen por módulo o carpeta |
| Huecos conocidos | Cola para consolidar |
| Historial | Trazabilidad instrucción → paths espejo |

## Ejemplo de ahorro

Tras 40 instrucciones de feature, el espejo puede tener ~80 % de rutas relevantes. Una consolidación con 15 paths en `paths_huecos` sustituye a un escaneo de 500+ archivos.

## Errores a evitar

- Pedir «genera toda la documentación integral» sin política previa → usar **consolidar**, no generar masivo.
- Cerrar instrucciones de código **sin** `espejo_actualizar` cuando la política está activa.
- Leer todo `50-sistema-integral/` para orientarse → usar registro + `espejo_leer` (≤3).

## Referencias

- Estrategia: [estrategia-instrucciones.md](../00-nucleo/estrategia-instrucciones.md)
- Flujo humano: [flujo-instrucciones-documentacion.md](flujo-instrucciones-documentacion.md)
- Espejo vs operativa: [sistema-integral-vs-detalle.md](sistema-integral-vs-detalle.md)
