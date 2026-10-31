---
id: auto.03.espejo-completo
stack: [cliente]
---

# 03: espejo-completo

## Fuente

`50-sistema-integral/`: el espejo replica el árbol del proyecto, un `.md`
por carpeta y por archivo de código.

## Valida

Paridad documentación ↔ código en ambas direcciones.

## Procedimiento

1. Listar archivos de código del proyecto (respetando exclusiones del
   `_PROTOCOLO.md` del espejo).
2. Verificar que cada uno tiene su `.md` espejo.
3. Verificar que cada `.md` espejo tiene su archivo de código vivo.

## Aceptación

- [ ] Cero archivos de código sin espejo.
- [ ] Cero espejos huérfanos (documentan algo que ya no existe).

## Salida

Dos listas: `código sin espejo` y `espejos huérfanos`.
