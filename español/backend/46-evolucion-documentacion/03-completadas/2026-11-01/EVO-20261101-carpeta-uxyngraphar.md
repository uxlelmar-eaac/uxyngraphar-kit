---
id: EVO-20261101-carpeta-uxyngraphar
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - AGENTES.md
  - scripts/carpeta_pack.py
  - scripts/nucleo/instalar.py
  - scripts/nucleo/clasificacion.py
  - scripts/nucleo/proteccion.py
  - scripts/nucleo/flujo.py
  - scripts/nucleo/mover.py
  - scripts/nucleo/transaccion.py
  - 10-guias/
proposed_at: 2026-11-01
instruction_derivada: solicitud-humana-20261101-carpeta-uxyngraphar
---
# EVO-20261101 — La carpeta del pack se llama `uxyngraphar/`

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita (uxlelmar, 2026-11-01): «Al momento de que se crea el contenido de nuestro sistema, lo crea en la carpeta Docs. Ya no quiero que la carpeta se llame Docs, quiero que sea una carpeta que haga referencia a uxyngraphar.» Nombre elegido: `uxyngraphar/`.

## Qué faltaba

El pack se instalaba siempre en `docs/`, un nombre genérico que choca con la documentación propia de muchos proyectos y no dice qué es. El instalador además exigía ese nombre.

## Decisión

- Las instalaciones nuevas van a `uxyngraphar/` (en un monorepo, `apps/<app>/uxyngraphar/`). El instalador acepta `uxyngraphar` o `docs` como último tramo (nada más: así la detección sigue siendo barata y no se confunde con carpetas del proyecto).
- Las instalaciones anteriores siguen en `docs/` y funcionan igual: el actualizador las reconoce por su lock y no crea una segunda copia. Las herramientas deducen la carpeta cuando no se indica `--docs` (`scripts/carpeta_pack.py`: la del propio script, la que tiene lock, la que existe, o `uxyngraphar`), y las rutas escritas en fichas valen con cualquiera de los dos prefijos.
- `AGENTES.md` habla de «la carpeta del pack» y escribe las rutas relativas a ella (sin subir el coste de arranque). Las guías del pack usan `uxyngraphar/` en sus ejemplos.
- Mover una instalación antigua de `docs/` a `uxyngraphar/` es opcional y lo decide una persona (`uxyngraphar mover-carpeta`, o el panel): nunca ocurre al actualizar.
- Sin cambios en el texto de las reglas R-xx.
