# Cambios

## 2.0.0

- uxyngraphar pasa de dos packs documentales (servidor/cliente) a un catálogo de paquetes de gobernanza temáticos, portátiles e inmutables: `ciclo-instrucciones`, `calidad-codigo`, `secretos`, `decisiones-adr`, `mapa-rutas-api`, `mapa-rutas-ui`, `areas-modulos`, `espejo-sistema`, `herramientas-autorizadas`, `auditorias`, `mejoras-pendientes`, `manuales`, `memoria-archivo`, `landing-page-bento` y `optimizacion-ux-eui`.
- En cada repo, una sola carpeta `uxyngraphar/` con `paquetes/` (instalados, inmutables), `trabajo/`, `INDICE.md` y `FLUJO.json` para decidir cómo trabaja el agente. Nada se activa solo: sin ganchos git ni puerta de commits.
- Fichas en `uxyngraphar/trabajo/<paquete>/[<tipo>/]<estado>/<id>.md`, sin números ni carpetas por fecha.
- Cada paquete: `README.md` (pasos + reglas), `paquete.json`, `docs/`, `plantillas/` y `scripts/` (los comunes en `scripts/comun/`).
- `uxyngraphar migrar` lleva instalaciones 1.x a 2.0 con simulación, respaldo, verificación sha256 y reversión.
- Se retiran los packs 1.x, su instalador por proyecto y su documentación.
