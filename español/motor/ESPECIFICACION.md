# Especificación — paquetes de gobernanza uxyngraphar 2.0

Validadores: [`motor/especificacion.py`](motor/especificacion.py) (paquete y flujo) y [`comun/uxyn_base.py`](comun/uxyn_base.py) (manifiesto e integridad; el mismo código viaja dentro de cada paquete).

## 1. Estructura en un repo

```
<raiz-app>/
  AGENTES.md · AGENTS.md          bloque generado entre <!-- uxyngraphar:inicio --> y <!-- uxyngraphar:fin -->
  uxyngraphar/                    todo uxyngraphar en una sola carpeta
    INDICE.md                     generado por el motor
    FLUJO.json                    lo edita solo una persona
    paquetes/<id>/                un paquete (inmutable; lo escribe solo el motor)
    trabajo/<id>/                 trabajo de cada paquete (editable)
      ajustes.json                opcional: sobrescribe «ajustes» del manifiesto
      <estado>/<ficha>.md         paquete con un solo tipo de ficha (p. ej. decisiones-adr/completadas/ADR-…md)
      <tipo>/<estado>/<ficha>.md  paquete con varios tipos (p. ej. ciclo-instrucciones/instrucciones/pendientes/INS-…md)
```

Sin números delante de las carpetas ni carpetas por fecha: la fecha va en el id de la ficha.

Un paquete resuelve su trabajo como `<carpeta-del-paquete>/../../trabajo/<id>/`.

## 2. Paquete

```
<id>/
  README.md                       lo único que lee el agente al activarlo: pasos y, al final, «## Reglas»
  paquete.json                    manifiesto (§3)
  INTEGRIDAD.json                 solo en paquetes construidos (§4)
  docs/  plantillas/              opcionales: guías y plantillas de fichas
  scripts/                        Python, solo librería estándar: los scripts propios del paquete
    comun/                        scripts comunes del kit (`comun/`), añadidos al construir; no van en el catálogo
      uxyn_base.py  uxyn_fichas.py  fichas.py  verificar.py  verificar-integridad.py
```

Requisitos de portabilidad:

- Ningún script importa nada de fuera de la carpeta del paquete ni supone rutas fijas del repo.
- Ningún script escribe fuera de `uxyngraphar/trabajo/<id>/` (salvo que la persona pase una ruta explícita).
- Nombres de archivo ASCII y sin espacios.
- Copiar la carpeta a otro `uxyngraphar/paquetes/` produce el mismo comportamiento.

## 3. Manifiesto `paquete.json`

| Campo | Tipo | Regla |
|-------|------|-------|
| `manifiesto_formato` | entero | `1` |
| `id` | texto | kebab-case ASCII; igual al nombre de la carpeta |
| `version` | texto | semver `X.Y.Z` |
| `titulo`, `descripcion` | texto | no vacíos |
| `motor` | texto | `>=X.Y`; versión mínima del motor |
| `activacion` | lista | frases que activan el paquete; incluye el `id` |
| `entrada` | texto | `README.md` |
| `verificaciones` | lista | `scripts/*.py` que el agente ejecuta antes de cerrar (la genérica: `scripts/comun/verificar.py`) |
| `fichas` | objeto | opcional; tipos de ficha (§3.1) |
| `ajustes` | objeto | opcional; valores por defecto que el proyecto puede sobrescribir en `ajustes.json` |

### 3.1 Tipos de ficha

```json
"fichas": {
  "adr": {
    "carpeta": ".",
    "prefijo": "ADR",
    "plantilla": "plantillas/adr.md",
    "inicial": "propuesta",
    "estados": {"propuesta": "pendientes", "aceptada": "completadas", "rechazada": "canceladas"},
    "solo_humano": ["aceptada", "rechazada"]
  }
}
```

Con varios tipos, cada uno tiene su carpeta:

```json
"fichas": {
  "instruccion": {
    "carpeta": "instrucciones",
    "prefijo": "INS",
    "plantilla": "plantillas/instruccion.md",
    "inicial": "awaiting_approval",
    "estados": {"awaiting_approval": "pendientes", "approved": "en-progreso", "done": "completadas"},
    "solo_humano": ["approved"]
  },
  "pregunta": {"carpeta": "preguntas", "prefijo": "PRE", "plantilla": "plantillas/pregunta.md", "inicial": "en-curso",
               "estados": {"en-curso": "en-curso", "completada": "completadas", "cancelada": "canceladas"}}
}
```

Un tipo plano usa `status_validos` en lugar de `estados`:

```json
"ruta": {"carpeta": ".", "prefijo": "RUT", "plantilla": "plantillas/ruta.md", "inicial": "activa", "status_validos": ["activa", "deprecada"]}
```

- `carpeta`: `.` (raíz del trabajo del paquete; solo si hay un único tipo) o un nombre kebab-case.
- Con `estados`: la ficha vive en `uxyngraphar/trabajo/<id>/<carpeta>/<carpeta-de-estado>/<ficha>.md`; las carpetas de estado son kebab-case sin números (`pendientes`, `en-progreso`, `completadas`, `archivadas`, `canceladas`, `para-eliminar`) y el `status` debe corresponder a la carpeta.
- Con `status_validos` (plana): vive en cualquier subruta de `<carpeta>/`.
- `solo_humano`: status que solo una persona puede poner (el agente nunca los asigna).
- Id de ficha nueva: `<PREFIJO>-<AAAAMMDD>-<slug>`.
- Las plantillas usan `{{id}}`, `{{fecha}}`, `{{titulo}}`, `{{status}}`.

## 4. `INTEGRIDAD.json`

```json
{"formato": 1, "algoritmo": "sha256", "paquete": "<id>", "version": "X.Y.Z", "archivos": {"<ruta>": "<sha256>"}}
```

Cubre todos los archivos del paquete salvo el propio `INTEGRIDAD.json`, `__pycache__/` y `*.pyc`. `scripts/comun/verificar-integridad.py` informa de archivos alterados, faltantes y añadidos; cualquiera de ellos es un fallo y el agente se detiene.

## 5. `FLUJO.json`

```json
{"formato": 1, "modo": "manual", "leer_por_defecto": [], "trabajar_con": null, "secuencia": [], "conflictos": "preguntar"}
```

| Modo | Comportamiento del agente |
|------|---------------------------|
| `manual` | Solo usa paquetes nombrados en el pedido. |
| `leer_por_defecto` | En cada pedido lee el `README.md` de `leer_por_defecto`; aplica solo los nombrados. |
| `trabajar_con` | Aplica `trabajar_con` cuando el pedido no nombra otro paquete; también lee `leer_por_defecto`. |
| `secuencia` | Recorre `secuencia` en orden (cada paquete con su `README.md` y sus verificaciones); también lee `leer_por_defecto`. |

- Un paquete nombrado en el pedido siempre se aplica, sea cual sea el modo.
- `conflictos: "preguntar"`: si dos paquetes activos se contradicen, el agente se detiene y pregunta.
- Todo id citado debe estar instalado.

## 6. Activación

El agente activa un paquete cuando el pedido contiene «usa el paquete <frase>» o «sigue el protocolo <frase>», con `<frase>` en `activacion`, o cuando `FLUJO.json` lo indica. Pasos:

1. `python3 uxyngraphar/paquetes/<id>/scripts/comun/verificar-integridad.py` → si falla, detenerse y avisar.
2. Leer `uxyngraphar/paquetes/<id>/README.md` (pasos y reglas).
3. Trabajar; escribir solo en `uxyngraphar/trabajo/<id>/`.
4. Ejecutar las `verificaciones` del manifiesto antes de terminar.

## 7. Versionado

- Cada paquete tiene su semver: MAYOR si cambia la forma del trabajo (`fichas`, carpetas), MENOR si añade reglas o guías, PARCHE si corrige.
- Actualizar reemplaza `uxyngraphar/paquetes/<id>/` completo; nunca toca `uxyngraphar/trabajo/`.
- Un cambio MAYOR que exija mover trabajo lo hace el motor con respaldo, nunca el paquete.

## 8. Migración desde 1.x

`uxyngraphar migrar --repo RUTA` busca instalaciones 1.x (`.uxyngraphar.lock` o numeración `00-nucleo`/`05-instrucciones`) en `docs/` o `uxyngraphar/` (hasta 4 niveles) y **solo simula**; `--aplicar` migra.

- Se bloquea (sin tocar nada) si no hay lock, si hay un archivo que la clasificación 1.x no cubre, un archivo de núcleo distinto del lock, `uxyngraphar/` junto a `docs/` o una carpeta `.uxyngraphar-migrando/` de una migración interrumpida.
- Contenido del proyecto (clases P/M/C) → `uxyngraphar/trabajo/<paquete>/` según la tabla de `migrar.DESTINOS` (`05-instrucciones/` → `ciclo-instrucciones/instrucciones/`, `20-decisiones/` → `decisiones-adr/`, `15-rutas/` → `mapa-rutas-api|ui/`, …); `0N-estado/<fecha>/x.md` pasa a `estado/x.md` (con la fecha delante solo si dos archivos chocan); lo que no tiene paquete y los artefactos locales (X: tokens de aprobación, lock) → `uxyngraphar/trabajo/_legado-1x/`. `uxyngraphar.config.json` se reparte en `ajustes.json`.
- Al aplicar: respaldo en `.uxyngraphar-respaldos/migracion-<fecha>/` (pack, AGENTES/AGENTS/CLAUDE, `.claude/settings.json`, CODEOWNERS, guardia de Cursor, exclusiones de IA, ganchos git) → copia a `.uxyngraphar-migrando/` → verificación sha256 → retirada del pack 1.x y de sus protecciones → el trabajo pasa a `uxyngraphar/trabajo/` (también cuando el pack 1.x vivía en `uxyngraphar/`) → instalación de los 12 paquetes equivalentes con `FLUJO.json` en `manual`. Cualquier fallo restaura el estado anterior desde el respaldo.
- `.gitignore`/`.gitattributes` con líneas del pack 1.x solo se avisan.
