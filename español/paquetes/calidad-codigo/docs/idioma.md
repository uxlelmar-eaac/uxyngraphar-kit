# Idioma del producto

- **Conversación:** en el idioma de la persona.
- **Producto:** código, identificadores, nombres de archivo, pruebas, commits y ramas en inglés y ASCII.
- **Texto visible para el usuario:** siempre por el sistema de i18n del proyecto (`locales/`, `i18n/`…), nunca escrito a mano en componentes.
- **Términos del dominio:** si el negocio usa una palabra propia (p. ej. «folio»), se usa solo si la persona la registró en un glosario del proyecto; si no, se traduce.
- **Excepciones:** código generado, migraciones históricas y archivos de traducción.

Ramas: `tipo/descripcion-corta` (`feat/checkout-coupons`). Commits: ver la regla 4 en `README.md`.
