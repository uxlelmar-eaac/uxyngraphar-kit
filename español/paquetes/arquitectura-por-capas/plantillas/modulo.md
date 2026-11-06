# Módulo nuevo: estructura

Sustituye `<nombre>`. Crea solo las capas que el módulo necesite; no dejes carpetas vacías.

## Servidor (`perfil: servidor`)

```
src/modules/<nombre>/
  <nombre>.module.ts        registro en el framework (si aplica)
  presentation/             controladores / handlers HTTP
  security/                 políticas del recurso
  sanitization/             limpieza de entrada (opcional)
  application/              casos de uso
  domain/                   reglas puras, sin IO
  infrastructure/           persistencia, clientes externos
  contracts/                DTOs compartidos (alineables con OpenAPI)
  integrations/             única frontera hacia otros módulos
```

## Cliente (`perfil: cliente`)

```
src/modules/<nombre>/
  api/          transporte HTTP (petición saliente, JSON crudo)
  reception/    adapta el JSON a la forma de vista (sin JSX)
  hooks/        estado remoto: orquesta api + reception
  components/   UI, sin lógica de red
  model/        utilidades puras (claves de consulta, formatos)
  types/        DTOs y view models
  integrations/ llamadas al api/ de otro módulo
  styles/       estilos de la funcionalidad
```

## Nombres de archivo

Relacionales: `<raiz>.<relacion>.<ext>` (`orders.controller.ts`, `orders.usecase.ts`, `orders.mapper.ts`, `orders.api.ts`, `orders.query-keys.ts`). Nunca `*-parte2`, `*-nuevo`, `utils2`.

## Al crear el módulo

- Si están instalados: su área (`mapa-de-modulos`), sus rutas (`rutas-de-api` o `paginas-de-interfaz`) y su espejo (`documentacion-espejo`).
- `capas.py revisar src/modules/<nombre>` sin infracciones.
