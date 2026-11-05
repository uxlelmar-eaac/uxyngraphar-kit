# uxyngraphar — kit (español)

Catálogo de **paquetes de gobernanza** para repos trabajados por personas y agentes de IA, y la herramienta que los instala.

```
español/
  uxyngraphar.py        el único comando: panel, catálogo, instalar/actualizar/quitar, flujo, migrar…
  VERSION               versión de la herramienta
  ESPECIFICACION.md     contrato de paquetes, FLUJO.json y migración desde 1.x
  CHANGELOG.md
  paquetes/             el catálogo: un paquete por carpeta (+ _fragmentos/, scripts comunes que se copian al construir)
  motor/                construir, instalar, generar INDICE/AGENTES/FLUJO, CLI y panel
    migracion/          migración de instalaciones 1.x
  distribucion/         instalador de una línea y publicación de releases
  pruebas/              pruebas de todo lo anterior
```

## En un repo

```
mi-repo/
  AGENTES.md                       bloque generado: cuándo mirar los paquetes
  uxyngraphar/                     paquetes instalados (inmutables) + INDICE.md
  uxyngraphar-work/                el trabajo del proyecto
    FLUJO.json                     cómo trabaja el agente (lo decide una persona)
    decisiones-adr/completadas/ADR-20261105-orm.md
    ciclo-instrucciones/instrucciones/pendientes/INS-20261105-landing.md
```

Ningún paquete actúa solo: el agente los usa cuando el pedido dice «usa el paquete X» / «sigue el protocolo X» o cuando `FLUJO.json` lo indica.

## Uso

```bash
python3 uxyngraphar.py                         # panel en el navegador
python3 uxyngraphar.py catalogo                # paquetes disponibles
python3 uxyngraphar.py instalar secretos ciclo-instrucciones --repo ../mi-app
python3 uxyngraphar.py flujo --repo ../mi-app --modo trabajar_con --trabajar-con ciclo-instrucciones
python3 uxyngraphar.py migrar --repo ../mi-app # instalación 1.x: simula; --aplicar migra con respaldo
python3 -m unittest discover -s pruebas -t pruebas
```

Crear o cambiar un paquete: en `paquetes/<id>/` (o desde la pestaña Catálogo del panel), subir su versión con `uxyngraphar.py version <id> menor` y actualizar los repos con `uxyngraphar.py actualizar --repo …`.
