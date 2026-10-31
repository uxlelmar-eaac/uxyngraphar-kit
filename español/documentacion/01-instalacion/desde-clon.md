# Instalar desde un clon del kit

Útil si desarrollas el kit o no quieres la herramienta global aún.

```bash
cd uxyngraphar-kit/español
python3 instalar.py
# Windows: py -3 instalar.py
```

Se abre una pantalla en tu navegador (solo en tu equipo) con 4 pasos: tu proyecto, qué instalar y dónde (servidor, cliente o ambos; un repo o dos), protección, y un **plan exacto antes de escribir nada**. Cada opción explica qué cambia si la eliges. Al terminar muestra lo que se hizo y qué sigue. Si el proyecto ya tiene uxyngraphar, ofrece actualizar sin tocar tu contenido. Requiere Python 3.10+ y git. Sin navegador:

```bash
python3 instalar.py --consola
```

Actualizar desde clon: se abre una pantalla con 3 pasos. Eliges uno o varios proyectos (detecta los packs instalados, también en monorepos), **revisas qué cambiaría** agrupado en lenguaje llano (archivos nuevos, actualizados, los que necesitan tu decisión con **comparación línea a línea**, plantillas con novedades, estado de salud) y confirmas. Antes de escribir hace copia de seguridad en `.uxyngraphar-respaldo/`, actualiza solo el núcleo (tu contenido no se toca) y añade las protecciones nuevas (CI, reglas de agentes, `.gitignore`…). Un salto de versión mayor pide el id de una instrucción aprobada.

```bash
python3 actualizar.py /ruta/al/proyecto
python3 actualizar.py /ruta --consola
python3 actualizar.py /ruta --si
```
