# uxyngraphar — kit (español)

Catálogo de **paquetes de gobernanza** para repos trabajados por personas y agentes de IA, y la herramienta que los instala.

```
español/
  motor/                  todo lo que instala, actualiza, configura y desinstala uxyngraphar
    uxyngraphar.py        el único comando: panel, catálogo, instalar/actualizar/quitar, flujo, migrar…
    VERSION               versión de la herramienta
    README.md  ESPECIFICACION.md  CHANGELOG.md
    cli.py catalogo.py especificacion.py repo.py generar.py panel.py panel.html
    migracion/            migración de instalaciones 1.x
    distribucion/         instalador de una línea y publicación de releases
    pruebas/              pruebas de todo lo anterior
  paquetes/               el catálogo: un paquete por carpeta, cada uno completo e independiente
    !base/                lo que se repite en todos: README.md, paquete.json, plantillas/ y scripts/comun/ (semilla de «crear»; no es un paquete)
```

Cada paquete lleva todo lo que necesita para funcionar y verificarse (también `scripts/comun/`): copiar su carpeta a otro
`uxyngraphar/paquetes/` basta. `validar` avisa, sin fallar, si su `scripts/comun/` difiere de `paquetes/!base/`.

## En un repo

```
mi-repo/
  AGENTES.md                       bloque generado: cuándo mirar los paquetes
  uxyngraphar/
    INDICE.md                      paquetes instalados y sus frases de activación (generado)
    FLUJO.json                     cómo trabaja el agente (lo decide una persona)
    paquetes/                      paquetes instalados (inmutables)
      secretos-y-credenciales/  README.md  paquete.json  INTEGRIDAD.json  docs/  scripts/  scripts/comun/
    trabajo/                       el trabajo del proyecto
      decisiones-de-arquitectura/completadas/ADR-20261105-orm.md
      instrucciones-aprobadas/instrucciones/pendientes/INS-20261105-landing.md
```

Ningún paquete actúa solo: el agente los usa cuando el pedido dice «usa el paquete X» / «sigue el protocolo X» o cuando `FLUJO.json` lo indica.

## Uso

Desde `español/` (instalado, basta `uxyngraphar …`):

```bash
python3 motor/uxyngraphar.py                         # panel en el navegador
python3 motor/uxyngraphar.py catalogo                # paquetes disponibles (con avisos)
python3 motor/uxyngraphar.py instalar secretos-y-credenciales instrucciones-aprobadas --repo ../mi-app --base instrucciones-aprobadas
python3 motor/uxyngraphar.py flujo --repo ../mi-app --modo leer_por_defecto --leer secretos-y-credenciales
python3 motor/uxyngraphar.py migrar --repo ../mi-app # instalación 1.x: simula; --aplicar migra con respaldo
python3 -m unittest discover -s motor/pruebas -t motor/pruebas
```

Crear o cambiar un paquete: en `paquetes/<id>/` (o desde la pestaña Catálogo del panel), subir su versión con `uxyngraphar.py version <id> menor` y actualizar los repos con `uxyngraphar.py actualizar --repo …`.
