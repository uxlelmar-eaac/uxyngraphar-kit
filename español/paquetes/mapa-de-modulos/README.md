# Mapa de módulos

Activado con «usa el paquete mapa-de-modulos» / «sigue el protocolo mapa de modulos» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/mapa-de-modulos/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Antes de cambiar algo, identifica el área: `python3 $S/comun/fichas.py listar area` y lee su contexto (`fichas.py ver <id>`); sigue su «Mapa de lectura».
4. Área nueva: `python3 $S/comun/fichas.py nueva area --slug <area> --en <area> --titulo "Área: …"`.
5. Si cambias fronteras, dependencias o código ancla de un área, actualiza su contexto en la misma tarea.
6. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-areas.py`.

Trabajo: `uxyngraphar/trabajo/mapa-de-modulos/<area>/`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Un contexto por área**, en su propia carpeta (`--en <area>`); el nombre de la carpeta es el nombre del área.
2. **Fronteras explícitas:** qué posee, qué no posee, dónde escribe datos y con qué externos habla.
3. **`depends_on`** lista nombres de áreas documentadas (carpetas); sin ciclos.
4. **Mapa de lectura corto** (≤5 pasos): lo mínimo que debe leer alguien para cambiar el área.
5. **Código ancla real:** carpetas o archivos existentes.
6. **Contexto vivo:** si cambian fronteras, dependencias o anclas, se actualiza en la misma tarea.
