# Áreas y módulos — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Un contexto por área**, en su propia carpeta (`--en <area>`); el nombre de la carpeta es el nombre del área.
2. **Fronteras explícitas:** qué posee, qué no posee, dónde escribe datos y con qué externos habla.
3. **`depends_on`** lista nombres de áreas documentadas (carpetas); sin ciclos.
4. **Mapa de lectura corto** (≤5 pasos): lo mínimo que debe leer alguien para cambiar el área.
5. **Código ancla real:** carpetas o archivos existentes.
6. **Contexto vivo:** si cambian fronteras, dependencias o anclas, se actualiza en la misma tarea.
