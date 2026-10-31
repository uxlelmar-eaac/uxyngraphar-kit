# Mantener y publicar el kit

Para quien trabaja en el repositorio fuente (`uxyngraphar-kit`). Todas las órdenes se ejecutan desde `español/`.

## Qué incluye cada pack

Instrucciones como contrato de tarea, reglas del proyecto propias del equipo (`96-reglas-proyecto/`, se aplican sin tocar las del núcleo), presupuesto de tokens, ciclo vinculante de actos, espejo 1:1 del código (`50-sistema-integral/`), colas de mejoras y evolución (`45`/`46`), herramientas autorizadas (`35`) y un panel de decisiones pendientes en Python (solo stdlib). Detalle completo en el `README.md` de cada pack ([servidor](../../backend/README.md) · [cliente](../../frontend/README.md)).

## Mantener los packs

- Lo idéntico en ambos packs se edita **solo** en `_compartido/base/` y se copia con `python3 _compartido/construir-packs.py` (`--verificar` en CI falla si hay deriva).
- Pruebas (las mismas que el CI):

```bash
python3 _compartido/construir-packs.py --verificar
python3 backend/scripts/ejecutar-pruebas.py
python3 frontend/scripts/ejecutar-pruebas.py
python3 backend/scripts/verificar-paridad.py
python3 -m unittest discover -s instalador -t instalador
python3 -m unittest discover -s _compartido -t _compartido
python3 _compartido/probar-actualizaciones.py
```

- **Solo Python para ejecutables:** todo script, instalador, actualizador o gancho de git del proyecto se escribe en Python (solo biblioteca estándar) para que funcione igual en Windows, macOS y Linux. No se añaden `.sh`, `.bat`, `.cmd`, `.ps1`, `.command` ni `.vbs`; en Windows se ejecutan con `py -3 <script>.py` o `python <script>.py`.
- **Reglas para que ninguna versión rompa una actualización** (sección «Garantías» de `10-guias/actualizar-nucleo.md` del pack):
  1. No quitar ni renombrar un script u opción de `scripts/nucleo/contrato.py`: la lista solo crece; un renombre deja el nombre viejo como alias.
  2. Si una versión cambia algo que los proyectos ya tienen (una clave de `uxyngraphar.config.json`, un archivo que se mueve), lo hace con una migración en `scripts/nucleo/migraciones.py` (idempotente, con prueba), nunca pidiéndoselo a la persona.
  3. Una sección nueva de la configuración entra con un valor por defecto que no cambia nada (`10-guias/configuracion-uxyngraphar.md` § «Cómo crece»).
  4. Antes de etiquetar: `python3 _compartido/probar-actualizaciones.py` (lo repite el CI): actualiza desde cada versión publicada y falla si algo se rompe.

## Versión

La versión vigente vive en `VERSION.md` de cada pack — **fuente única** — y su historial en el `CHANGELOG.md` del pack. Ambos packs se versionan en espejo: se editan en `_compartido/base/` y se copian con `construir-packs.py`.

## Publicar una versión

1. Subir `VERSION.md` + `CHANGELOG.md` en `_compartido/base/` y la línea **Versión:** del `README.md` de cada pack; reconstruir con `construir-packs.py`; pasar las pruebas; commit.
2. Etiquetar: `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. El workflow `.github/workflows/publicar.yml` pasa las pruebas en Linux, macOS y Windows, ejecuta `_compartido/publicar.py` (zip, instalador de una línea y `SHA256SUMS`) y crea la release: desde ese momento el comando de una línea instala esa versión. El repositorio debe ser público.

Para probar la publicación en local: `python3 _compartido/publicar.py --salida dist`.

## Gobernanza

- Estructura del pack **intocable por IA** sin instrucción `approved` derivada de una ficha `EVO-*` (regla R-14).
- Paridad entre packs: `backend/PARIDAD-PACKS.md` + `python3 backend/scripts/verificar-paridad.py` (solo en este repo; no se instala en proyectos).
- Validación documental: `python3 scripts/validar-documentacion.py` dentro del pack (ver `10-guias/ci-validacion-documentacion.md`).
