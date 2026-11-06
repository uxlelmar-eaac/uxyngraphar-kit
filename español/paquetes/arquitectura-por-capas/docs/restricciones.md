# Restricciones de arquitectura

Ninguna se rompe sin una ADR aceptada por una persona.

## Servidor

1. **Cruces de módulo solo por `integrations/`:** la capa de aplicación no importa servicios de otros módulos; llama a `../integrations/<dominio>.integration` con métodos de propósito claro (`ensureXExists`, `notifyY`).
2. **Dominio puro:** sin framework, ORM ni IO en `domain/`; se prueba sin infraestructura.
3. **El código común no importa módulos de negocio.** Configuración, logging, acceso a datos y filtros globales viven en lo común.
4. **Variables de entorno validadas al arrancar:** fallar pronto si falta una.
5. **Webhooks firmados:** cuerpo en bruto y verificación de firma antes de interpretar el JSON.

## Cliente

1. **Separar transporte de adaptación:** `api/` habla con el servidor; `reception/` adapta la respuesta; los componentes no hacen red.
2. **Sin acoplar dominios:** no importar hooks ni componentes de otro módulo salvo lo compartido (`common/`, layouts, props).
3. **Estilos acotados** a la funcionalidad; los globales en lo común.
4. **Solo variables públicas en el cliente** (p. ej. `NEXT_PUBLIC_*`), validadas; nunca claves del servidor.
5. **No duplicar el catálogo HTTP del servidor:** el cliente cita sus ids (ver `contratos-entre-repos` si está instalado).

## Proyecto existente

Con `nivel: aviso` (por defecto), las infracciones se listan sin bloquear: regístralas como deuda y corrígelas por tandas. Cuando el código esté limpio, una persona sube `nivel` a `bloqueante`.
