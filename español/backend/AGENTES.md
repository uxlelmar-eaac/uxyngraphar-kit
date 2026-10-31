# AGENTES.md — servidor

Punto de entrada. Lee **solo esto** (+ `docs/ESTADO.md`). Detalle bajo demanda: `docs/00-nucleo/agentes-detalle.md`. (`AGENTS.md` es un alias.)

## Flujo
(`docs/` = la carpeta junto a este archivo; en un monorepo, la de tu app.)
1. ¿Hay ficha `docs/35-herramientas/autorizadas/<id>.md` con `status: authorized` que cubra el pedido? → ejecútala (solo ficha + anclas).
2. Si no: pedido vago o nuevo → crea la instrucción `awaiting_approval` (`python3 docs/scripts/decisiones/decisiones.py new instruccion --slug <slug>`) y **espera aprobación**. Sin `status: approved` no se edita código ni docs.
3. Con instrucción aprobada: `python3 docs/scripts/contexto.py <id>` imprime todo lo necesario (ficha, lectura mínima, anclas con rango). **No abras nada más.**
4. Implementa solo dentro de `anclas_codigo`. Al verificar y al cerrar, marca la fase: `python3 docs/scripts/costo-tokens.py fase <id> verificacion|cierre`. Al cerrar: escribe `espejo_actualizar` y ejecuta `python3 docs/scripts/decisiones/decisiones.py cerrar <id>` (escribe el costo en tokens).

## Límites
- Presupuesto: ≤8 docs y ≤5 archivos de código por tarea. Máx. 350 líneas por archivo de código (R-19; división con nombre relacional).
- ¿Más de 5 archivos de código? (R-21) Justifica en `Alcance` si es sumamente necesario. No lo es → fracciona en instrucciones de ≤5 (`fraccion_de`, `depende_de`). Lo es → `ampliacion_factor` 1.5–2 (tope 7–10) + `ampliacion_justificacion` y **espera aprobación humana** antes de codear. Guía: `docs/00-nucleo/ampliacion-alcance.md`.
- Idioma (R-22): conversa en el idioma del humano, pero código, archivos, commits (`feat(scope): …`) y ramas del producto van en inglés y ASCII; término local solo si está en `docs/00-nucleo/glosario-dominio.md`; texto para el usuario por i18n. `docs/` sigue en su idioma.
- Nombres (R-23): cada identificador dice qué es y para qué sirve sin comentario (intención, dominio, unidad: `timeoutMs`, `isActive`, `ORDER_STATUS.SHIPPED`); comentarios solo para el porqué. Guía: `docs/00-nucleo/nombres-autoexplicativos.md`.
- Deuda o bug fuera de alcance → ficha en `docs/45-mejoras-propuestas/01-pendientes/` (≤3); **no la implementes**. Gap del sistema documental → ficha `EVO-*` en `docs/46-evolucion-documentacion/01-pendientes/` (≤2). Nunca docs funcionales en 46 (R-18).
- Cada commit pasa por `docs/scripts/controlar.py` (líneas, anclas, secretos, núcleo); si bloquea, corrige el cambio, no la puerta ni `uxyngraphar.config.json`.
- Al cambiar `status`, mueve la ficha a su carpeta de estado (R-17). Secretos: solo `<PLACEHOLDER>`; nunca leas ni crees `.env`/llaves (el commit las bloquea).
- Memoria (R-24): nunca leas, busques ni ejecutes nada en `docs/95-memoria/`; si una tarea la necesita, pídelo en la instrucción.
- Reglas del proyecto: `docs/96-reglas-proyecto/INDICE.md`; cúmplelas. Excepción (`excepciones_reglas`) o cambio de reglas: solo con instrucción aprobada por una persona.
- Ajustes locales (R-25): si `docs/97-ajustes-locales/INDICE.md` lista un ajuste activo para un archivo del núcleo que usas, síguelo; donde se contradigan, manda el ajuste. No crees ni edites ajustes, ni actives o ejecutes `feedback.py`: eso lo hace una persona.
- No leer `docs/INDICE.md`, `PROTOCOLO.md`, `10-guias/`, `90-archivo/` ni volcar `50-sistema-integral/` (usa `espejo-mapa.py`). No escribir en `35-herramientas/autorizadas/` ni ejecutar `propuestas/`.

## Núcleo de solo lectura (R-20)
No editar, borrar, renombrar ni crear archivos en: `AGENTES.md`, `AGENTS.md`, `docs/REGLAS.md`, `docs/PROTOCOLO.md`, `docs/00-nucleo/` (salvo `configuracion-proyecto`, `arquitectura`, `restricciones`, `registro-ids-compartidos`, `mapa-dependencias`), `docs/10-guias/`, `docs/55-automatizaciones/`, `docs/scripts/`, `_PLANTILLA*`, `_PROTOCOLO*`; tampoco `.uxyngraphar.lock`, `.claude/settings.json`, `CODEOWNERS`, CI ni ganchos git, ni evites la verificación. Mejora al sistema → solo ficha `EVO-*`. Si el núcleo aparece alterado, **detente y avisa al humano**.
