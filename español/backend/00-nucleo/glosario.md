# Glosario (servidor)

| Término | Significado |
|---------|-------------|
| Núcleo | Reglas vigentes en `00-nucleo/` |
| Instrucción | Orden humana en `05-instrucciones/`; contrato de lectura IA |
| Lectura mínima | Lista cerrada de docs en frontmatter de instrucción |
| Ancla | Path de código autorizado para abrir (con rango opcional) |
| Presupuesto | Máx. docs/archivos por tarea (default 8/5) |
| Área | Dominio de negocio con `25-areas/<id>/CONTEXTO.md` |
| Ficha de endpoint | Documento de una ruta HTTP en `15-rutas/` |
| ADR | Decisión arquitectónica en `20-decisiones/` |
| Auditoría | Investigación en `40-auditorias/` |
| Integración | Adaptador hacia otro módulo o servicio externo |
| Presentación | Capa HTTP de entrada al servidor |
| Dominio | Reglas puras sin framework ni persistencia |
| Webhook | Notificación HTTP de un servicio externo |
| Bandeja de eventos (inbox) | Eventos externos pendientes de procesar |
| Cuerpo en bruto (raw body) | Petición sin parsear (útil para verificar firmas) |

Términos de **negocio** del proyecto (los que pueden aparecer en el código según R-22): [glosario-dominio.md](glosario-dominio.md). Este glosario es del pack (congelado); aquel lo completa el proyecto.
