# 0006 · Otros idiomas: un motor compartido y un catálogo por idioma

- **Estado:** aceptada (diseño; sin implementar). Nota 2026-11-11: el catálogo se llama hoy `sistemas-de-gobernanza/` y los sistemas se sirven desde el servidor (ADR 0007); el idioma pasa a ser un campo del sistema (`idioma`, ADR 0008).
- **Fecha:** 2026-11-10

## Contexto

Hoy el kit solo existe en español y su estructura (`español/motor/`, `español/sistemas-de-gobernanza/`) anticipa otros idiomas sin decir cómo convivirían. Antes de añadir uno hay que fijar qué se comparte y qué no, para no duplicar el motor ni mezclar normas de nombres.

## Decisión

1. **Un único motor compartido.** La lógica (instalar, actualizar, transacciones, panel) no depende del idioma. Sus mensajes pasan a catálogos de textos por idioma cuando haga falta el segundo idioma.
2. **Un catálogo por carpeta de idioma.** Cada idioma tiene su carpeta en la raíz del repositorio (`español/sistemas-de-gobernanza/`, por ejemplo `english/governance-systems/`) con su `_base` y sus sistemas. Un sistema pertenece a un idioma y no se traduce en su sitio: su versión en otro idioma es otro sistema con su propio id.
3. **Norma de nomenclatura por idioma.** Cada catálogo lleva su `NOMENCLATURA.md` y su `nomenclatura.json` (vocabulario de status, palabras de función, frases de activación). La regla «nombres ASCII, kebab-case» es común; el vocabulario no.
4. **El idioma se elige al instalar.** El instalador pregunta el idioma (o lo toma de `--idioma`) y lo guarda en `casa.json`; el panel y la CLI usan ese catálogo. Un proyecto puede tener sistemas de un solo idioma a la vez, que es el de su `uxyngraphar/`.

## Consecuencias

- La carpeta `español/` sigue siendo la del primer idioma y no se renombra (ver NOMENCLATURA, «Excepción de nombre»).
- Cuando llegue el segundo idioma: mover el motor a una carpeta común (`motor/` en la raíz) con un período en que el instalador y `publicar.py` acepten ambas rutas, añadir `--idioma` al instalador y separar los textos del motor.
- Hasta entonces no se implementa nada de esto.
