# Calidad de código — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Límite de líneas.** Ningún archivo de código supera `limite_lineas` (350) líneas físicas. Si un cambio lo supera, se divide por responsabilidad con **nombre relacional** (`order-service.ts` → `order-service.pricing.ts`, `order-service.validation.ts`). Exenciones solo las declara una persona en `exenciones_lineas`.
2. **Nombres autoexplicativos.** Cada identificador dice qué es y para qué sirve, con unidad o dominio cuando aplica (`timeoutMs`, `isActive`, `ORDER_STATUS.SHIPPED`). Prohibidos `data`, `tmp`, `obj`, `x`, `handle2`. Comentarios solo para el porqué.
3. **Idioma del producto.** Código, nombres de archivo, identificadores, mensajes de commit y ramas en inglés y ASCII. El texto que ve el usuario va por i18n. Términos del dominio en otro idioma solo si la persona los fijó en un glosario.
4. **Commits.** Formato Conventional Commits: `tipo(ámbito): resumen` con `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` o `revert`; resumen en imperativo, en inglés, ≤72 caracteres.
5. **No se debilita la revisión.** El agente no edita `ajustes.json`, ni añade exclusiones o exenciones para que `revisar.py` pase.
