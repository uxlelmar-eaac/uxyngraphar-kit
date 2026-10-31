# Guías (servidor)

| Guía | Uso |
|------|-----|
| [incorporacion.md](incorporacion.md) | Incorporación y arranque local |
| [instalacion-docs.md](instalacion-docs.md) | **Scaffolding:** pegar pack (una vez) + smoke |
| [elegir-pack.md](elegir-pack.md) | Qué pack instalar según el tipo de aplicación |
| [control-de-construccion.md](control-de-construccion.md) | Puerta `controlar.py`: límite de líneas, anclas, secretos, núcleo |
| [configuracion-uxyngraphar.md](configuracion-uxyngraphar.md) | **Archivo de configuración del proyecto** (`uxyngraphar.config.json`): cada sección, valores por defecto y cómo crece |
| [costo-tokens.md](costo-tokens.md) | Costo en tokens de cada instrucción, por fases (`costo-tokens.py`) |
| [respaldos.md](respaldos.md) | Copias de seguridad: dónde quedan, cuánto se conservan, restaurar y limpiar (`respaldos.py`) |
| [memoria.md](memoria.md) | **Memoria del sistema** (R-24): nada se borra; las fichas terminan en `95-memoria/`, que solo consulta el humano (`memoria.py`) |
| [ajustes-locales.md](ajustes-locales.md) | **Ajustes locales** (R-25): aplicar una EVO aprobada en el proyecto sin tocar el núcleo (`ajustes.py`) |
| [envio-sugerencias.md](envio-sugerencias.md) | **Envío de sugerencias** (opcional, apagado por defecto): mandar las fichas de 46 a quien mantiene uxyngraphar (`feedback.py`) |
| [adopcion-pack.md](adopcion-pack.md) | Roadmap primer mes |
| [flujo-instrucciones-documentacion.md](flujo-instrucciones-documentacion.md) | Pedido → instrucción → sync docs + espejo |
| [pruebas.md](pruebas.md) | Cómo probar |
| [contratos-api.md](contratos-api.md) | OpenAPI / contratos HTTP |
| [sync-documentacion-pr.md](sync-documentacion-pr.md) | Checklist PR + promoción auditoría |
| [sync-multi-repo.md](sync-multi-repo.md) | PRs backend ↔ frontend separados |
| [monorepo-docs-fusionados.md](monorepo-docs-fusionados.md) | Docs unificados (opcional) |
| [generar-documentacion-integral.md](generar-documentacion-integral.md) | Espejo 1:1 (instrucción IA) |
| [espejo-incremental-proyectos-grandes.md](espejo-incremental-proyectos-grandes.md) | **Acumulación incremental** — política + consolidar huecos |
| [sistema-integral-vs-detalle.md](sistema-integral-vs-detalle.md) | Espejo vs operativa |
| [herramientas-autorizadas-vs-propuestas.md](herramientas-autorizadas-vs-propuestas.md) | Autorizadas vs propuestas |
| [mejoras-propuestas-ia.md](mejoras-propuestas-ia.md) | **Cola deuda/mejoras** — registrar sin ejecutar |
| [ciclo-integral-actos.md](ciclo-integral-actos.md) | **Actos vinculantes** — matriz acto × carpeta |
| [tarjeta-referencia-humana.md](tarjeta-referencia-humana.md) | **Referencia 1 página** — pedir → aprobar → revisión de pendientes |
| [redaccion-lectura-minima.md](redaccion-lectura-minima.md) | Cómo declarar `lectura_minima` (tokens) |
| [organizacion-estados-fechas.md](organizacion-estados-fechas.md) | **Estados + fechas** — estructura de secciones acumulativas (R-17, R-18) |
| [ci-validacion-documentacion.md](ci-validacion-documentacion.md) | CI estricto (`STRICT_*`) |
| [!00_banco-documentacion-practica.html](../!00_banco-documentacion-practica.html) | **Diagrama visual** — flujo documental en 1 scroll |

Validación opcional: [../scripts/validar-documentacion.py](../scripts/validar-documentacion.py).
