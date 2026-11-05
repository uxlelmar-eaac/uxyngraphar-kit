# Espejo del sistema — entrada

Activado con «usa el paquete espejo-sistema» / «sigue el protocolo espejo» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/espejo-sistema/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/espejo-sistema/REGLAS.md`.
3. Para entender código, lee primero su espejo: `python3 $S/espejo.py ver <ruta-del-codigo>`. Mapa y cobertura: `python3 $S/espejo.py mapa [--faltantes]`.
4. Al crear, mover o cambiar la responsabilidad de un archivo o carpeta, crea o actualiza su espejo en la misma tarea: `python3 $S/espejo.py nuevo <ruta-del-codigo>`.
5. Al borrar código, borra su espejo (`python3 $S/espejo.py huerfanos` los lista).
6. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-espejo.py`.

Trabajo: `uxyngraphar-work/espejo-sistema/<ruta-del-codigo>.md` (archivo) y `…/<carpeta>/README.md` (carpeta).
