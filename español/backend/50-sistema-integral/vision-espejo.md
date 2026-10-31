# Visión — documentación integral como espejo

## Qué es

La documentación integral **no es otra taxonomía** (dominios, contratos sueltos, etc.). Es una **copia estructural** del proyecto: mismas carpetas, mismos nombres de ruta, pero en lugar de código hay textos `.md` que explican el sistema.

## Para qué sirve

- Onboarding: recorrer el repo como si fuera el código, leyendo explicaciones.
- Mapa mental: ver de un vistazo cómo está organizado el scaffolding real.
- Puente con `25-areas/`: el CONTEXTO apunta anclas de código; el espejo explica **contexto humano** de cada carpeta/archivo.

## Qué va aquí vs en otras carpetas

| Espejo (`50-sistema-integral/`) | `25-areas/` | `15-rutas/` |
|---------------------------------|-------------|-------------|
| Estructura idéntica al proyecto | Agrupación por dominio para IA | Ficha HTTP |
| README por carpeta, .md por archivo | CONTEXTO, mapa de lectura | Contrato request/response |
| Sin presupuesto de tokens en tareas puntuales | Lectura habitual en implementación | Citada desde CONTEXTO |

## Generación

Se asume una **instrucción aprobada** que ordena: escanear scaffolding → replicar carpetas → escribir solo `.md`.

| Enfoque | Plantilla |
|---------|-----------|
| Proyecto pequeño / espejo vacío | `_PLANTILLA-generar-espejo-integral.md` |
| Proyecto mediano+ (recomendado) | `_PLANTILLA-politica-espejo-incremental.md` + sync en cada `_PLANTILLA.md` |
| Doc general con mapa parcial | `_PLANTILLA-consolidar-espejo-integral.md` |

Ver [espejo-incremental-proyectos-grandes.md](../10-guias/espejo-incremental-proyectos-grandes.md).
