# Calidad de código

Activado con «usa el paquete calidad-de-codigo» / «sigue el protocolo calidad de codigo» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/calidad-de-codigo/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo); guías en `docs/` (`limite-lineas.md`, `nombres.md`, `idioma.md`).
3. Mientras trabajas, aplica las reglas a todo lo que escribas. Términos del dominio sin traducir permitidos: `python3 $S/glosario.py terminos`.
4. Antes de terminar: `python3 $S/calidad.py` (todo) o `python3 $S/calidad.py <archivos>` (solo los tuyos); `--commits` revisa también los últimos mensajes de commit.
   - Un archivo que tú hiciste crecer por encima del límite se divide en esta misma tarea (guía `limite-lineas.md`).
   - Un archivo que ya excedía y no tocaste: avísalo, no lo dividas por tu cuenta.

Persona: `uxyngraphar/trabajo/calidad-de-codigo/ajustes.json` (`raices`, `extensiones`, `excluir`, `limite_lineas`, `exenciones_lineas`) y el glosario `uxyngraphar/trabajo/calidad-de-codigo/GLOSARIO.md` (`python3 $S/glosario.py iniciar` lo crea vacío).

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Límite de líneas.** Ningún archivo de código supera `limite_lineas` (350) líneas físicas. Si un cambio lo supera, se divide por responsabilidad con **nombre relacional** (`order-service.ts` → `order-service.pricing.ts`, `order-service.validation.ts`). Exenciones solo las declara una persona en `exenciones_lineas`.
2. **Nombres autoexplicativos.** Cada identificador dice qué es y para qué sirve, con unidad o dominio cuando aplica (`timeoutMs`, `isActive`, `ORDER_STATUS.SHIPPED`). Prohibidos `data`, `tmp`, `obj`, `x`, `handle2`. Comentarios solo para el porqué.
3. **Idioma del producto.** Código, nombres de archivo, identificadores, mensajes de commit y ramas en inglés y ASCII. El texto que ve el usuario va por i18n. Términos del dominio en otro idioma solo si están en `GLOSARIO.md` (ASCII, casing del código, sin conjugar); el agente no lo edita. Código antiguo en otro idioma: no se renombra de paso (guía `idioma.md`).
4. **Commits.** Formato Conventional Commits: `tipo(ámbito): resumen` con `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` o `revert`; resumen en imperativo, en inglés, ≤72 caracteres.
5. **No se debilita la revisión.** El agente no edita `ajustes.json`, ni añade exclusiones o exenciones para que `calidad.py` pase.
