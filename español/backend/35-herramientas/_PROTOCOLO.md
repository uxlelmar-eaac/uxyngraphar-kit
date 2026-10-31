# Protocolo — herramientas

## Rol

Catálogo de artefactos reutilizables (scripts, comandos, snippets, plantillas de codegen) que **agilizan** trabajo repetitivo sin sustituir instrucciones para cambios de producto.

## Reglas duras

1. **Autorizadas:** creación **solo humana** (manual o promoción desde propuesta aprobada). `autorizadas/` es un registro **sin estados**.
2. **Propuestas:** creación **solo IA** dentro de instrucción o documentada en Resultado al cerrar; **nunca ejecutar** el código sugerido. Organización por estados (R-17):

```
35-herramientas/propuestas/
├── 01-pendientes/YYYY-MM-DD/   ← pending
├── 02-en-progreso/             ← en-evaluacion (humano revisando)
├── 03-completadas/             ← (la promovida sale a autorizadas/)
├── 04-archivadas/              ← archivada
├── 05-canceladas/YYYY-MM-DD/   ← rejected
└── 06-listas-para-eliminar/    ← para-eliminar
```

3. **Ejecución sin instrucción** (excepción): solo si:
   - Ficha en `autorizadas/` con `status: authorized`
   - Ficha listada en `autorizadas/INDICE.md`
   - Pedido humano coincide con alcance de la ficha
   - Agente lee **solo esa ficha** (≤2 docs) + `anclas_codigo` de la ficha
4. **Promoción:** propuesta `approved` → humano crea ficha en `autorizadas/` (`source: human`); la propuesta original queda marcada y fuera de `01-pendientes/`.
5. **Rechazo:** mover a `propuestas/05-canceladas/YYYY-MM-DD/` con `status: rejected`.
6. **No duplicar** `30-manuales/` (procedimientos ops) ni `10-guias/` (onboarding).

## Fichas

- Plantilla autorizada: [_PLANTILLA-autorizada.md](_PLANTILLA-autorizada.md)
- Plantilla propuesta: [_PLANTILLA-propuesta.md](_PLANTILLA-propuesta.md)
- Promoción: [_PLANTILLA-promover-desde-propuesta.md](_PLANTILLA-promover-desde-propuesta.md)
- El código vive en el repo; la ficha describe cuándo y cómo usarlo.

## IA

- No listar ni volcar todo `35-herramientas/`.
- No escribir en `autorizadas/` (salvo que la instrucción sea explícitamente redactar propuesta para humano).
- Propuestas: registrar path en `herramientas_propuestas` del frontmatter de instrucción.

Ver [estrategia-instrucciones.md](../00-nucleo/estrategia-instrucciones.md) · [herramientas-autorizadas-vs-propuestas.md](../10-guias/herramientas-autorizadas-vs-propuestas.md).
