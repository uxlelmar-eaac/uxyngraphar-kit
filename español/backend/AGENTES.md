# AGENTES.md — servidor

Punto de entrada. Lee **solo esto** (+ `ESTADO.md`). Detalle bajo demanda: `00-nucleo/agentes-detalle.md`. (`AGENTS.md` es un alias.)

## Flujo
(Rutas relativas a la carpeta del pack: `uxyngraphar/` junto a este archivo, o `docs/` si se instaló antes de la 1.1.0; en un monorepo, la de tu app.)
Un pedido que termina en «sigue el protocolo <frase>» pide este flujo (por defecto: uxyngraphar, uxyn, uxynar; las del proyecto, en la línea «Activación» de `ESTADO.md`), aunque la frase llegue con otra grafía.
1. ¿Hay ficha `35-herramientas/autorizadas/<id>.md` con `status: authorized` que cubra el pedido? → ejecútala (solo ficha + anclas).
2. Si no: pedido vago o nuevo → crea la instrucción `awaiting_approval` (`python3 uxyngraphar/scripts/decisiones/decisiones.py new instruccion --slug <slug>`) y **espera aprobación** (la persona la aprueba en su panel: `uxyngraphar` → Proyecto → Pendientes). Sin `status: approved` no se edita código ni docs.
3. Con instrucción aprobada: `python3 uxyngraphar/scripts/contexto.py <id>` imprime todo lo necesario (ficha, lectura mínima, anclas con rango). **No abras nada más.**
4. Implementa solo dentro de `anclas_codigo`. Al verificar y al cerrar, marca la fase: `python3 uxyngraphar/scripts/costo-tokens.py fase <id> verificacion|cierre`. Al cerrar: escribe `espejo_actualizar` y ejecuta `python3 uxyngraphar/scripts/decisiones/decisiones.py cerrar <id>` (escribe el costo en tokens).

## Límites
- Presupuesto: ≤8 docs y ≤5 archivos de código por tarea. Máx. 350 líneas por archivo de código (R-19; división con nombre relacional).
- ¿Más de 5 archivos de código? (R-21) Justifica en `Alcance` si es sumamente necesario. No lo es → fracciona en instrucciones de ≤5 (`fraccion_de`, `depende_de`). Lo es → `ampliacion_factor` 1.5–2 (tope 7–10) + `ampliacion_justificacion` y **espera aprobación humana** antes de codear. Guía: `00-nucleo/ampliacion-alcance.md`.
- Idioma (R-22): conversa en el idioma del humano, pero código, archivos, commits (`feat(scope): …`) y ramas del producto van en inglés y ASCII; término local solo si está en `00-nucleo/glosario-dominio.md`; texto para el usuario por i18n. La carpeta del pack sigue en su idioma.
- Nombres (R-23): cada identificador dice qué es y para qué sirve sin comentario (intención, dominio, unidad: `timeoutMs`, `isActive`, `ORDER_STATUS.SHIPPED`); comentarios solo para el porqué. Guía: `00-nucleo/nombres-autoexplicativos.md`.
- Deuda o bug fuera de alcance → ficha en `45-mejoras-propuestas/01-pendientes/` (≤3); **no la implementes**. Gap del sistema documental → ficha `EVO-*` en `46-evolucion-documentacion/01-pendientes/` (≤2). Nunca docs funcionales en 46 (R-18).
- Cada commit pasa por `scripts/controlar.py` (líneas, anclas, secretos, núcleo); si bloquea, corrige el cambio, no la puerta ni `uxyngraphar.config.json`.
- Al cambiar `status`, mueve la ficha a su carpeta de estado (R-17). Secretos: solo `<PLACEHOLDER>`; nunca leas ni crees `.env`/llaves (el commit las bloquea).
- Memoria (R-24): nunca leas, busques ni ejecutes nada en `95-memoria/`; si una tarea la necesita, pídelo en la instrucción.
- Reglas del proyecto: `96-reglas-proyecto/INDICE.md`; cúmplelas. Excepción (`excepciones_reglas`) o cambio de reglas: solo con instrucción aprobada por una persona.
- Ajustes locales (R-25): si `97-ajustes-locales/INDICE.md` lista un ajuste activo para un archivo del núcleo que usas, síguelo; donde se contradigan, manda el ajuste. No crees ni edites ajustes, ni actives o ejecutes `feedback.py`: eso lo hace una persona.
- No leer `INDICE.md`, `PROTOCOLO.md`, `10-guias/`, `90-archivo/` ni volcar `50-sistema-integral/` (usa `espejo-mapa.py`). No escribir en `35-herramientas/autorizadas/` ni ejecutar `propuestas/`.
- Si arrancas un servidor, un watcher u otra instancia para probar, ciérrala antes de terminar el turno. No dejes procesos ocupando puertos ni ralentizando a la persona. Si el puerto ya está en uso, no levantes otra copia.

## Núcleo de solo lectura (R-20)
No editar, borrar, renombrar ni crear archivos en: `AGENTES.md`, `AGENTS.md`, `REGLAS.md`, `PROTOCOLO.md`, `00-nucleo/` (salvo `configuracion-proyecto`, `arquitectura`, `restricciones`, `registro-ids-compartidos`, `mapa-dependencias`), `10-guias/`, `55-automatizaciones/`, `scripts/`, `_PLANTILLA*`, `_PROTOCOLO*`; tampoco `.uxyngraphar.lock`, `.claude/settings.json`, `CODEOWNERS`, CI ni ganchos git, ni evites la verificación. Mejora al sistema → solo ficha `EVO-*`. Si el núcleo aparece alterado, **detente y avisa al humano**.
