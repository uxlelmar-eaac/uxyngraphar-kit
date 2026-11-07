# Mapa de módulos

Mantiene un contexto por área funcional —propósito, fronteras, dependencias, mapa de lectura y código ancla— para que cualquier cambio empiece por el área correcta y sepa qué leer, con dependencias entre áreas sin ciclos.

## Qué resuelve

En un sistema mediano nadie tiene en la cabeza qué parte del código es responsable de qué. Los cambios empiezan leyendo carpetas al azar, una responsabilidad acaba repartida entre dos áreas y las dependencias se cierran en ciclo sin que nadie lo decida. Este paquete da a cada área una ficha corta que dice qué posee y qué no, de qué otras áreas depende y por dónde empezar a leer, y comprueba que el grafo de dependencias no tenga ciclos ni huecos.

## Problemas que cubre

- `cambios-sin-area-identificada`: cambios que empiezan sin saber a qué área pertenecen ni qué leer.
- `fronteras-de-area-difusas`: áreas sin declarar qué poseen, qué no, dónde escriben y con qué externos hablan.
- `dependencias-entre-areas-circulares`: ciclos en `depends_on`.
- `dependencias-hacia-areas-sin-documentar`: `depends_on` hacia áreas sin contexto.
- `contextos-de-area-desfasados`: fronteras, dependencias o código ancla que ya no corresponden al código.

## Fuera de alcance

- Imports entre módulos y entre capas: `arquitectura-monolitica-por-capas`.
- Documentar cada archivo o carpeta: `documentacion-espejo`.
- Decidir partir, fusionar o crear un área que condiciona el sistema: `decisiones-de-arquitectura`.
- Contratos HTTP entre repositorios: `contratos-entre-repositorios`.
- Organigrama del equipo y responsables fuera del código: no lo cubre el kit.

## Cuándo usarlo

- Antes de empezar un cambio en código que no conoces: para saber en qué área cae y qué leer.
- Al crear un área funcional nueva o cambiar sus fronteras.
- Al añadir o quitar una dependencia entre áreas.
- Al incorporar a alguien (persona o agente) a un sistema existente.

## Cuándo no usarlo

- En proyectos con una sola área funcional.
- Para describir la estructura interna de un módulo (capas, archivos): eso lo hacen otros paquetes.

## Entradas y salidas

- Entradas: el código, el pedido y los contextos existentes en `uxyngraphar/trabajo/mapa-de-modulos/`.
- Salidas: contextos `ARE-…` en `uxyngraphar/trabajo/mapa-de-modulos/<area>/` y el informe de `verificar-areas.py` (ciclos y dependencias sin documentar).

## Paquetes complementarios

- `arquitectura-monolitica-por-capas`: impone en el código las fronteras que aquí se describen.
- `documentacion-espejo`: el mapa de lectura apunta a los espejos de los archivos clave.
- `decisiones-de-arquitectura`: la ADR que crea, parte o fusiona un área.
- `rutas-de-api`: los endpoints que posee cada área.
