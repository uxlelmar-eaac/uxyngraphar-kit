# Plantilla de módulo del servidor (capas + integraciones)

Úsala para **cada nuevo módulo de negocio**. Sustituye `<nombre>` y las rutas por las del proyecto.

## Árbol orientativo

```
src/modules/<nombre>/          # adaptar a la convención del proyecto
  <punto-entrada-modulo>       # registro del módulo en el framework (si aplica)
  presentation/                # controladores / handlers HTTP
  security/                   # políticas del recurso
  sanitization/               # opcional
  application/                # casos de uso
  domain/                     # reglas puras, sin IO
  infrastructure/             # persistencia, clientes externos
  contracts/                  # DTOs compartidos
  integrations/               # frontera hacia otros módulos
```

## Convenciones

1. **`integrations/`**: métodos de propósito claro (`ensureXExists`, `notifyY`); no acceso libre a servicios ajenos desde `application/`.
2. **`domain/`**: tipos y funciones testeables sin IO.
3. **`contracts/`**: lo que capas de entrada y aplicación comparten; alineable con OpenAPI.

## Código transversal

Ver [arquitectura.md](arquitectura.md) sección de código común.

## Límite 350 líneas (R-19)

Cada archivo del módulo ≤350 líneas físicas (`wc -l`). Si un archivo lo supera, dividir con nomenclatura relacional (`<raiz>.<relacion>.<ext>`: `.controller`, `.service`, `.usecase`, `.repository`, `.schema`, `.mapper`, `.dto`, `.policy`, `.integration`) antes de cerrar el PR. Prohibido `*-parte2`, `*-nuevo`, `utils2`. Detalle: [limite-350-lineas.md](limite-350-lineas.md).

## Sincronización documental

Módulo nuevo → también crear:

- `docs/25-areas/<nombre>/CONTEXTO.md`
- `docs/15-rutas/<nombre>/` (+ INDICE local si aplica)
- Fila en `docs/25-areas/INDICE.md`
