# Sistema integral — espejo documental del proyecto
<!-- uxyngraphar:inicio -->

**Carpeta única** para documentar **todo el proyecto** replicando su estructura de carpetas. No contiene código: solo archivos `.md` que explican qué hace cada parte del scaffolding real.

## Idea central

```
<repo>/src/modules/auth/auth.service.ts     ← código (fuera de docs/)
docs/50-sistema-integral/src/modules/auth/    ← misma ruta relativa
  README.md                                   ← qué es esta carpeta
  auth.service.md                             ← qué hace este archivo (sin copiar código)
```

La documentación integral **no inventa otra taxonomía**: copia el árbol del proyecto y lo rellena con explicación.

## Meta (prefijo `_`)

| Archivo | Uso |
|---------|-----|
| [_PROTOCOLO.md](_PROTOCOLO.md) | Reglas del espejo, nomenclatura, exclusiones |
| [_PLANTILLA-README-carpeta.md](_PLANTILLA-README-carpeta.md) | Plantilla por carpeta |
| [_PLANTILLA-archivo.md](_PLANTILLA-archivo.md) | Plantilla por archivo de código |
| [vision-espejo.md](vision-espejo.md) | Por qué existe y relación con `25-areas/` |
| [mapa-capas.md](mapa-capas.md) | Enlace al espejo del otro repo (multi-repo) |

## Generar el espejo (primera vez o resync)

1. Rellenar raíces y exclusiones en [`00-nucleo/configuracion-proyecto.md`](../00-nucleo/configuracion-proyecto.md).
2. Crear instrucción desde [`05-instrucciones/_PLANTILLA-generar-espejo-integral.md`](../05-instrucciones/_PLANTILLA-generar-espejo-integral.md).
3. Tras aprobación, la IA recorre el scaffolding, replica carpetas y escribe solo `.md`.
4. Guía humana: [generar-documentacion-integral.md](../10-guias/generar-documentacion-integral.md).

## Cuándo leer esta carpeta

| Tarea | Entrada |
|-------|---------|
| Cambio local en un módulo | `25-areas/` + `15-rutas/` |
| Entender **dónde vive algo** o el **mapa completo** del repo | Espejo bajo `50-sistema-integral/<ruta-proyecto>/` |
| Onboarding / visión de producto | `README.md` de carpetas raíz del espejo |

## Relación con otras carpetas

```
50-sistema-integral/   ← espejo 1:1 del scaffolding (explicación, sin código)
25-areas/              ← capacitación IA por dominio (CONTEXTO, anclas)
15-rutas/              ← fichas HTTP
```

Repo cliente: misma idea en su propio `docs/50-sistema-integral/` (espejo del frontend).

## IA — bajo tokens

No volcar el espejo entero. La instrucción cita paths concretos del espejo (p. ej. un `README.md` o un `.md` de archivo). Ver [eficiencia-ia.md](../00-nucleo/eficiencia-ia.md).
<!-- uxyngraphar:fin -->

<!-- Debajo de esta línea es tuyo: al actualizar uxyngraphar solo cambia lo que está entre los marcadores de arriba. -->
