# uxyngraphar — kit (español)

Catálogo de **paquetes especializados** para repos trabajados por personas y agentes de IA, y la herramienta que los instala.
Cada paquete es un **entorno de trabajo completo** para un conjunto acotado de problemas: qué resuelve y qué no, sus límites,
su proceso por fases, sus skills, sus herramientas, su andamiaje y sus ejemplos, todo dentro de su carpeta.

```
español/
  motor/                  todo lo que instala, actualiza, configura y desinstala uxyngraphar
    uxyngraphar.py        el único comando: panel, catálogo, instalar/actualizar/quitar, flujo, andamiar, migrar…
    VERSION               versión de la herramienta
    README.md  ESPECIFICACION.md  NOMENCLATURA.md  GUIA-DE-PAQUETES.md  CHANGELOG.md
    cli.py catalogo.py especificacion.py piezas.py entrada.py andamiaje.py nomenclatura.py repo.py generar.py panel.py …
    migracion/            migración de instalaciones 1.x
    distribucion/         instalador de una línea y publicación de releases
    pruebas/              pruebas de todo lo anterior
  paquetes/               el catálogo: un paquete por carpeta, cada uno completo e independiente
    !base/                el protocolo: núcleo (paquete.json, README.md, PAQUETE.md), scripts/comun/ y piezas/<pieza>/ (semillas; no es un paquete)
```

## El protocolo de paquetes

`paquetes/!base/` rige **la estructura**, no el contenido (contrato completo en [`ESPECIFICACION.md`](ESPECIFICACION.md) §2;
criterio de diseño en [`GUIA-DE-PAQUETES.md`](GUIA-DE-PAQUETES.md)):

- **Núcleo obligatorio:** `paquete.json` (con `alcance`: problemas que cubre y lo que deriva a otros paquetes), `README.md`
  (bloque de entrada generado + texto libre) y `PAQUETE.md` (la descripción del paquete) más `scripts/comun/`.
- **Piezas estándar opcionales**, con forma fija y declaradas en `piezas`: `limites` (`LIMITES.md`), `proceso` (`proceso/<fase>.md`),
  `skills` (`skills/<nombre>/SKILL.md`), `componentes`, `herramientas`, `andamiaje`, `plantillas`, `referencia`, `ejemplos`,
  `pruebas` y `cambios` (`CHANGELOG.md`).
- **Extensiones libres**, declaradas en `extensiones` con su propósito: lo que no encaje en una pieza.

Solo es error lo que rompe la estructura (núcleo, piezas declaradas frente a presentes, forma de cada pieza, entradas sin declarar);
lo demás son avisos (más de 5 problemas, problemas sin cubrir, piezas recomendadas para la familia). Agregar, quitar o actualizar
una pieza es un comando; quitar un paquete es borrar su carpeta.

Cada paquete lleva todo lo que necesita para funcionar y verificarse: copiar su carpeta a otro `uxyngraphar/paquetes/` basta.
Las skills viven solo dentro del paquete (el agente las lee desde ahí; nada se copia a `.cursor/` ni `.claude/`).
Los nombres siguen [`NOMENCLATURA.md`](NOMENCLATURA.md); `validar` y `crear` la comprueban.
El paquete de referencia es [`arquitectura-monolitica-por-capas`](../paquetes/arquitectura-monolitica-por-capas/PAQUETE.md), que usa todas las piezas.

## En un repo

```
mi-repo/
  AGENTES.md                       bloque generado: cuándo mirar los paquetes
  uxyngraphar/
    INDICE.md                      paquetes instalados, frases de activación y problemas que cubren (generado)
    FLUJO.json                     cómo trabaja el agente (lo decide una persona)
    paquetes/                      paquetes instalados (inmutables)
      arquitectura-monolitica-por-capas/  README.md  PAQUETE.md  LIMITES.md  proceso/  skills/  andamiaje/  …  INTEGRIDAD.json
    trabajo/                       el trabajo del proyecto
      decisiones-de-arquitectura/completadas/ADR-20261105-orm.md
      instrucciones-aprobadas/instrucciones/pendientes/INS-20261105-landing.md
```

Ningún paquete actúa solo: el agente los usa cuando el pedido dice «usa el paquete X» / «sigue el protocolo X» o cuando
`FLUJO.json` lo indica. Entonces sigue el bloque de entrada del README del paquete: integridad, `PAQUETE.md` (si el pedido
está fuera de alcance, deriva), `LIMITES.md`, las fases de `proceso/` en orden y las skills que cada fase cita.

## Uso

Desde `español/` (instalado, basta `uxyngraphar …`):

```bash
python3 motor/uxyngraphar.py                         # panel en el navegador
python3 motor/uxyngraphar.py catalogo                # paquetes disponibles (con avisos)
python3 motor/uxyngraphar.py validar --completitud   # piezas de cada paquete y recomendadas que faltan
python3 motor/uxyngraphar.py instalar secretos-y-credenciales instrucciones-aprobadas --repo ../mi-app --base instrucciones-aprobadas
python3 motor/uxyngraphar.py andamiar arquitectura-monolitica-por-capas modulo-servidor --nombre orders --repo ../mi-app   # simula; --aplicar crea
python3 motor/uxyngraphar.py flujo --repo ../mi-app --modo leer_por_defecto --leer secretos-y-credenciales
python3 motor/uxyngraphar.py migrar --repo ../mi-app # instalación 1.x: simula; --aplicar migra con respaldo
python3 -m unittest discover -s motor/pruebas -t motor/pruebas
```

Crear o cambiar un paquete (o desde la pestaña Catálogo del panel):

```bash
python3 motor/uxyngraphar.py crear contratos-de-pago --titulo "Contratos de pago" --familia arquitectura --piezas limites,proceso,skills,cambios
python3 motor/uxyngraphar.py pieza contratos-de-pago agregar ejemplos   # o: quitar <pieza>
python3 motor/uxyngraphar.py indice-paquete contratos-de-pago           # tras editar paquete.json a mano
python3 motor/uxyngraphar.py version contratos-de-pago menor
python3 motor/uxyngraphar.py actualizar --repo ../mi-app
```

Un paquete recién creado no valida hasta rellenar los marcadores `{{…}}` de su núcleo (`PAQUETE.md` y `alcance`).
