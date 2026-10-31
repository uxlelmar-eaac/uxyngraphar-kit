# Plantilla de funcionalidad del cliente (capas + integraciones)

Úsala para **cada nuevo dominio** bajo la carpeta de módulos/features del proyecto. Sustituye `<nombre>` y rutas según el stack.

## Simetría con el servidor

En el servidor, la capa de **entrada HTTP** recibe lo que envía el cliente.

En el cliente, lo que **entra** desde el servidor es la respuesta HTTP. La carpeta **`reception/`** (o equivalente) adapta ese JSON antes de hooks y componentes.

- **`api/`**: transporte; petición saliente y JSON entrante (a menudo crudo).
- **`reception/`**: mapeos y esquemas; sin JSX ni hooks de datos.

## Árbol orientativo

```
src/modules/<nombre>/
  api/
    get-<recurso>.api.ts
    create-<recurso>.api.ts
  reception/
    map-<recurso>.mapper.ts
    validate-<recurso>.schema.ts
  hooks/
    use-<recurso>.query.ts
    use-create-<recurso>.mutation.ts
  components/
    <Recurso>List.tsx
  guards/                     # opcional
  styles/
    <recurso>-list.module.css
  model/
    <recurso>.query-keys.ts
  types/
    <recurso>.dto.ts
    <recurso>.view.ts
  integrations/
    <otro-dominio>.integration.ts
```

### Equivalencia conceptual con servidor

| Servidor | Cliente |
|---------|----------|
| `presentation/` | `reception/` |
| `application/` | `hooks/` |
| `domain/` | `model/` |
| `infrastructure/` | `api/` |
| `contracts/` | `types/` + esquema generado si aplica |

## Convenciones

1. **`api/`**: solo HTTP; sin JSX; sin hooks de caché/consulta.
2. **`reception/`**: mappers/esquemas; sin hooks de datos.
3. **`hooks/`**: orquestan `api` + `reception`.
4. **`components/`**: estilos desde carpeta de estilos de la funcionalidad.
5. **`integrations/`**: un archivo por dominio externo; solo hacia `api/` ajeno.
6. **Carpeta común del proyecto**: cliente HTTP, config, UI genérica.

## Lista de verificación en PR

- ¿Import a otro módulo fuera de `integrations/`? → Corregir.
- ¿Nuevas variables de entorno? → config central del proyecto.
- ¿Contratos API? → regenerar tipos y alinear `types/` + `reception/`.
- ¿Algún archivo >350 líneas físicas (`wc -l`)? → Dividir con nomenclatura relacional antes de cerrar (R-19, [limite-350-lineas.md](limite-350-lineas.md)).

## Sincronización documental

Dominio nuevo → `docs/25-areas/<nombre>/CONTEXTO.md` + fila en índice de áreas.
