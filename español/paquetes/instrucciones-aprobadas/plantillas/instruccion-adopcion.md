---
id: {{id}}
status: {{status}}
source: human
tipo: adopcion
created: {{fecha}}
approved_at: null
executed_at: null
ampliacion_factor: null
ampliacion_justificacion: null
lectura_minima: []
anclas_codigo: []
fases: [escaneo, configuracion, modulos-iniciales, documentacion-base, comprobacion]
---

# {{titulo}}

<!-- Primera vez en un repo: con o sin documentación previa. Se aprueba completa y se ejecuta por fases;
     si una fase supera el alcance, se fracciona en instrucciones hijas (`fraccion_de`). -->

## Objetivo
Al cerrar: paquetes instalados y configurados, 1–2 módulos documentados, verificaciones en verde.

## Fase 1 — Escaneo
- [ ] Stack, punto de entrada y carpetas de negocio (`src/…`, `package.json`/`pyproject.toml`…)
- [ ] Documentación previa: qué hay y qué se conserva

## Fase 2 — Configuración
- [ ] `ajustes.json` de los paquetes que lo necesiten (raíces, perfil de capas, límites) — los escribe la persona
- [ ] Paquete base y modo en `FLUJO.json` — los decide la persona

## Fase 3 — Módulos iniciales
- [ ] Ficha de 1–2 áreas (`mapa-de-modulos`) con su código ancla
- [ ] Sus rutas (`rutas-de-api` o `paginas-de-interfaz`)

## Fase 4 — Documentación base
- [ ] Espejo de los archivos clave, si `documentacion-espejo` está instalado
- [ ] ADR de las decisiones ya tomadas que sigan vigentes (propuestas: las acepta la persona)

## Fase 5 — Comprobación
- [ ] `verificar.py` y las verificaciones de cada paquete instalado, sin errores
- [ ] Resumen de huecos para la persona (posibles EVO o mejoras)

## Fuera de alcance
- (lo detectado que no se hace aquí)

## Decisión (persona)
- Aprobar: `python3 uxyngraphar/paquetes/instrucciones-aprobadas/scripts/ciclo.py aprobar {{id}} --humano`
- Cancelar: `python3 uxyngraphar/paquetes/instrucciones-aprobadas/scripts/comun/fichas.py estado {{id}} cancelled`
