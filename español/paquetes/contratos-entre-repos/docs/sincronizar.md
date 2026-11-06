# Sincronizar repos que comparten una API

## Orden

1. **Proveedor primero:** el repo que sirve la API documenta la ruta (`rutas-de-api`) y su contrato `rol: proveedor`, y se fusiona.
2. **Consumidor después:** crea su contrato `rol: consumidor` con el mismo `id_compartido`, cita `ficha_proveedor` (URL o ruta en el otro repo) e implementa. No cierres su PR antes de que el del proveedor esté fusionado.
3. Los dos regeneran su `REGISTRO.md` (`contratos.py registro`).

## Lista para el PR del consumidor

- [ ] Contrato `consumidor` con `id_compartido`, `method`, `path`, `version` y `ficha_proveedor`.
- [ ] `contratos.py comparar` sin divergencias (si el repo proveedor está al lado).
- [ ] Sin copiar la ficha ni el OpenAPI del proveedor: se cita.
- [ ] Tipos regenerados si el proveedor publica OpenAPI ([contratos-api.md](contratos-api.md)).
- [ ] Un manejador propio del cliente (BFF) lleva su contrato `rol: bff` y, si hay `paginas-de-interfaz`, su ficha allí.

## Cambios incompatibles

- Nueva `version` del contrato y convivencia de las dos mientras haya consumidores en la anterior.
- El proveedor marca la vieja `deprecado`; la retira (`retirado`, decisión de una persona) cuando ningún consumidor vigente la usa.
- Renombrar un `id_compartido` es un cambio incompatible: contrato nuevo y retirada del anterior.

## Repo aislado

Cada repo tiene todo lo que necesita en su `uxyngraphar/`. No se abre el otro repo salvo para `comparar` o si el pedido lo pide.
