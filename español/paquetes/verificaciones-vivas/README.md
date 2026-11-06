# Verificaciones vivas

Activado con «usa el paquete verificaciones-vivas» / «sigue el protocolo verificaciones vivas» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/verificaciones-vivas/scripts`.

Contrasta lo documentado por los demás paquetes con el código real. **Solo se ejecuta cuando alguien lo pide**: no es puerta de commit ni de CI.

| Revisión | Compara | Necesita |
|----------|---------|----------|
| `rutas` | rutas del código (Nest, Express, Fastify, FastAPI, Flask) ↔ fichas | `rutas-de-api` |
| `paginas` | páginas `app/**/page.*` (Next) ↔ fichas | `paginas-de-interfaz` |
| `anclas` | rutas citadas en secciones «… ancla» y campos `campos_ancla` ↔ archivos | — |
| `decisiones` | ADR `aceptada` con `comprobacion_prohibido` (y `aplica_a`) ↔ código | `decisiones-de-arquitectura` |
| `manuales` | manuales `vigente`: `ultima_verificacion` y rutas citadas | `manuales-operativos` |
| `vinculos` | ids citados (`XXX-AAAAMMDD-slug`) ↔ fichas existentes | — |
| `humo` | comandos de `humo` en ajustes; solo con `--ejecutar` | — |

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Ejecuta lo pedido: `python3 $S/vivas.py [revisión…]` (sin revisión: todas menos `humo`).
4. Para dejar constancia: añade `--informe`. Con `auditorias-tecnicas` instalado nace una auditoría (`AUD-…-vivas-…`, status `activa`) con la tabla de hallazgos; si no, `uxyngraphar/trabajo/verificaciones-vivas/INFORME-<fecha>-<revisiones>.md`.
5. Presenta los hallazgos a la persona; las correcciones van por el flujo normal (instrucción, mejora o ADR).
6. Al terminar: `python3 $S/comun/verificar.py`.

Persona: `raices`, `excluir`, `prefijo_global` (p. ej. `api` si el servidor lo añade), `dias_manual` y `humo` (`[{"nombre": "…", "comando": "…", "segundos": 300}]`) en `uxyngraphar/trabajo/verificaciones-vivas/ajustes.json`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Solo lectura:** las revisiones no corrigen nada; reportan. La única que ejecuta es `humo`, y solo con `--ejecutar`.
2. **Bajo pedido:** no se encadenan a commits, CI ni a otras tareas sin que la persona lo pida.
3. **Humo sin efectos reales:** los comandos apuntan a entornos de prueba o modo simulación; nunca a producción.
4. **Hallazgos con evidencia** (`archivo:línea`), en tabla; la prosa solo en recomendaciones.
5. **Un hallazgo no es una corrección:** cada uno se resuelve por su propio flujo y con la aprobación que corresponda.
