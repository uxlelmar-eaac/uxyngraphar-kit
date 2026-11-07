# Límites

Se cumplen en todo el trabajo del paquete.

1. **Un contexto por área**, en su propia carpeta (`--en <area>`); el nombre de la carpeta es el nombre del área.
2. **Fronteras explícitas:** qué posee, qué no posee, dónde escribe datos y con qué externos habla.
3. **`depends_on`** lista nombres de áreas documentadas (carpetas); sin ciclos.
4. **Mapa de lectura corto** (≤5 pasos): lo mínimo que debe leer alguien para cambiar el área.
5. **Código ancla real:** carpetas o archivos existentes.
6. **Contexto vivo:** si cambian fronteras, dependencias o anclas, se actualiza en la misma tarea.
7. **No inventes `owners`:** los pone la persona; si no se conocen, la lista queda vacía.

## Cuándo detenerse y preguntar

- El cambio no encaja en ningún área documentada (¿área nueva o ampliación de una existente?).
- Corregir un ciclo de dependencias exige mover responsabilidades entre áreas.
- Dos áreas declaran poseer lo mismo (una tabla, un endpoint, un flujo).
- El pedido parte o fusiona áreas: la decisión es de una persona.
