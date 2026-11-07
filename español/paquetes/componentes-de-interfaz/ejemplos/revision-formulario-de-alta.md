# Caso: unificar el formulario de alta

## Pedido

«Usa el paquete componentes-de-interfaz: el alta no se parece al resto de la app; revísala.» El proyecto no tiene `INTERFAZ.md` todavía.

## Recorrido

**inventariar.** Se copia `$P/plantillas/INTERFAZ.md` a `uxyngraphar/trabajo/componentes-de-interfaz/INTERFAZ.md`. Los tokens están en `src/styles/tokens.css`; los componentes compartidos, en `src/ui/`:

```
| Color      | src/styles/tokens.css | --color-primario, --color-superficie, --color-texto, --color-error |
| Espaciado  | src/styles/tokens.css | 4 · 8 · 12 · 16 · 24 · 32 |
| Button | src/ui/Button.tsx | acción primaria y secundaria (variant) |
| Field  | src/ui/Field.tsx  | campo con etiqueta y mensaje de error |
```

**revisar.** Se abre `## Revisión 2026-11-06 — /signup`. Con `revisar-consistencia` salen tres hallazgos:

```
| 1 | /signup | valor-suelto      | Azul del botón escrito a mano               | `src/signup/form.module.css:12` (`#3b82f6`) | Token `--color-primario`              | | pendiente |
| 2 | /signup | duplicado         | Botón propio en lugar de `Button`           | `src/signup/SubmitButton.tsx:1`             | `Button` de `src/ui/Button.tsx`      | | pendiente |
| 3 | /signup | estado-sin-cubrir | El envío no muestra carga ni se deshabilita | enviar con red lenta: se puede pulsar 3 veces | Prop `loading` de `Button`        | | pendiente |
```

Un margen de `18px` en la página de inicio de sesión queda en «Notas»: no está en el pedido. El agente se detiene y resume los tres hallazgos; la persona marca «sí» en los tres.

**corregir.** `SubmitButton` se sustituye por `Button` con `loading` mientras se envía (cubre carga y deshabilitado; normal, hover, foco y activo ya los da `Button`); el color suelto desaparece con él. Se vuelve a aplicar `revisar-consistencia` sobre `src/signup/`: sin hallazgos nuevos. Los tres pasan a `corregido`; `verificar.py` sin errores.

## Resultado

- `INTERFAZ.md` con el inventario y la revisión del alta: tres hallazgos `corregido`.
- El margen del inicio de sesión queda en «Notas» para una revisión futura; no se tocó.
