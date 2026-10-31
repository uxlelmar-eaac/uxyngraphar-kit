# Sistema integral — espejo documental del proyecto (cliente)
<!-- uxyngraphar:inicio -->

**Estructura idéntica al scaffolding del frontend**, solo archivos `.md`.

## Idea central

```
<repo>/src/app/dashboard/page.tsx          ← código
docs/50-sistema-integral/src/app/dashboard/  ← misma ruta
  README.md
  page.md
```

## Meta (prefijo `_`)

| Archivo | Uso |
|---------|-----|
| [_PROTOCOLO.md](_PROTOCOLO.md) | Reglas del espejo (capa UI) |
| [_PLANTILLA-README-carpeta.md](_PLANTILLA-README-carpeta.md) | Por carpeta |
| [_PLANTILLA-archivo.md](_PLANTILLA-archivo.md) | Por componente/archivo |
| [vision-espejo.md](vision-espejo.md) | Relación con `25-areas/` |
| [mapa-capas.md](mapa-capas.md) | Enlace al espejo backend |

## Generar el espejo

1. Configurar raíces en [`00-nucleo/configuracion-proyecto.md`](../00-nucleo/configuracion-proyecto.md).
2. Instrucción: [`05-instrucciones/_PLANTILLA-generar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md).
3. Guía: [generar-documentacion-integral.md](../10-guias/generar-documentacion-integral.md).

## Cuándo leer

| Tarea | Entrada |
|-------|---------|
| Cambio UI / BFF local | `25-areas/` |
| Mapa completo del frontend | Espejo bajo `50-sistema-integral/` |
| Endpoint API | Ficha en **repo servidor**; aquí citar id en `.md` |

Ver [_PROTOCOLO.md](_PROTOCOLO.md) y [eficiencia-ia.md](../00-nucleo/eficiencia-ia.md).
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
