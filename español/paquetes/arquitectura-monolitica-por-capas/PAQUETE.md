# Arquitectura monolítica por capas

Mantiene un monolito modular sano: cada módulo de negocio aislado de los demás, capas internas con dependencias en un solo sentido y código común libre de negocio. Se comprueba leyendo los imports, sin ejecutar el proyecto.

## Qué resuelve

En un monolito, el acoplamiento crece en silencio: un caso de uso importa el servicio de otro módulo, el dominio acaba dependiendo del ORM y una utilidad común arrastra medio negocio. Cada atajo funciona hoy y encarece cada cambio de mañana. Este paquete fija un perfil de capas (servidor o cliente), crea los módulos nuevos ya con esa forma y detecta cada import que lo rompe.

## Problemas que cubre

- `modulos-acoplados`: módulos que se importan entre sí sin pasar por `integrations/`.
- `capas-mal-importadas`: capas que importan otras que su perfil no permite (por ejemplo, `domain` → `infrastructure`).
- `comun-dependiente-del-negocio`: código común que importa módulos de negocio.
- `modulos-sin-estructura-uniforme`: módulos nuevos que nacen sin las capas del perfil.

## Fuera de alcance

- Decidir y registrar una excepción de arquitectura (la ADR que la autoriza): `decisiones-de-arquitectura`.
- Describir áreas funcionales, sus fronteras y su mapa de lectura: `mapa-de-modulos`.
- Documentar cada archivo o carpeta: `documentacion-espejo`.
- Contratos HTTP entre repositorios: `contratos-entre-repositorios`.
- Arquitecturas distribuidas (microservicios, colas entre servicios): no lo cubre el kit.

## Cuándo usarlo

- Al crear un módulo de negocio nuevo.
- Al mover código entre módulos o entre capas.
- Al revisar un cambio que añade imports entre carpetas de `src/modules/`.
- Al adoptar el perfil en un proyecto existente (diagnóstico inicial con `nivel: aviso`).

## Cuándo no usarlo

- En scripts sueltos, prototipos desechables o repositorios sin módulos de negocio.
- Para decidir si conviene partir el monolito en servicios.

## Entradas y salidas

- Entradas: el código bajo `raices` (por defecto `src/`), los ajustes del proyecto en `uxyngraphar/trabajo/arquitectura-monolitica-por-capas/ajustes.json` (`perfil`, `nivel`, `modulos`, `comun`, `alias`) y, si existe, `ARQUITECTURA.md` del proyecto.
- Salidas: módulos con la estructura del perfil, imports corregidos, el informe de `capas.py revisar` y, cuando se acepta una desviación, su anotación en `ARQUITECTURA.md`.

## Paquetes complementarios

- `decisiones-de-arquitectura`: la ADR que autoriza romper una restricción.
- `mapa-de-modulos`: el contexto de cada área que este paquete estructura.
- `deuda-y-mejoras`: la cola donde se registran las infracciones heredadas para corregirlas por tandas.
- `documentacion-espejo`: la ficha de cada archivo del módulo nuevo.
