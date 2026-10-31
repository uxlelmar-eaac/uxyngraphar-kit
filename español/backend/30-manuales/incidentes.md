# Incidentes (servidor)

1. Acotar área afectada y abrir auditoría en `40-auditorias/02-en-progreso/YYYY-MM-DD/` si la investigación no es trivial.
2. Revisar logs del servicio y últimos despliegues.
3. Para integraciones externas (webhooks, colas): revisar bandeja de eventos y herramientas de reproceso si existen.
4. Al cerrar: archivar auditoría y promocionar hallazgos permanentes a canon / ADR / ficha.
