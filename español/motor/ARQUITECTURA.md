# Arquitectura del motor

Cómo se organiza el código de `motor/` y qué pasa cuando se cambia un proyecto. Para el contrato de los sistemas, ver [`ESPECIFICACION.md`](ESPECIFICACION.md).

## Módulos

```
            uxyngraphar.py (entrada: herramienta) ──► cli.py (comandos de sistemas y proyectos)
                    │                                    │
        panel.py ── rutas_panel.py (API) ────────────────┤
                    │                                    ▼
                    │      repo.py (instalar, actualizar, quitar, retirar, reparar, verificar)
                    │        │        │            │             │
                    │        ▼        ▼            ▼             ▼
                    │  transaccion.py  generar.py  protecciones.py  catalogo.py ──► especificacion.py, piezas.py,
                    │  (respaldo,      (INDICE,    (reglas deny,    (listar,          nomenclatura.py, entrada.py
                    │   candado,        bloque de   exclusiones      construir,       └► sistemas-de-gobernanza/_base/scripts/comun/
                    │   deshacer)       agentes,    de IA)           crear)              uxyn_base.py (manifiesto,
                    │                   FLUJO)                                           integridad)
                    ▼
  proyectos.py · grupos.py · flujos_guardados.py · herramienta.py · reparacion.py · desinstalacion.py
  diagnostico.py · vocabulario.py · integracion.py · auditoria.py · procesos.py · casa.py (carpeta de datos)
  distribucion/ (instalador de una línea, accesos directos, publicar.py)
```

- **Entrada.** `uxyngraphar.py` atiende las órdenes de la herramienta (versión, actualizar, usar, reparar, desinstalar) y pasa el resto a `cli.py`. El panel (`panel.py`) sirve `web/` y la API de `rutas_panel.py`; las dos vías llaman a las mismas funciones.
- **Proyecto.** `repo.py` es el único que cambia `uxyngraphar/sistemas-de-gobernanza/`; todo cambio pasa por `transaccion.transaccion()`. `generar.py` escribe lo generado (INDICE.md, bloque de agentes, FLUJO.json inicial) y `protecciones.py` las barreras pasivas.
- **Catálogo.** `catalogo.py` lista, crea, edita, versiona y construye sistemas (con `scripts/comun/` copiado de `_base`). La validación está en `especificacion.py` (estructura), `piezas.py` (una función por pieza) y `nomenclatura.py` (nombres y vocabulario).
- **Equipo.** `casa.py` es la carpeta de datos (`~/.uxyngraphar` o `UXYNGRAPHAR_HOME`): proyectos, grupos, flujos guardados, respaldos, registros y huellas. Nada de esto vive en los repos.

## Ciclo de vida de una transacción

1. **Candado.** `transaccion.candado()` crea `.bloqueo` (O_EXCL) junto a los respaldos del proyecto con el pid, el hilo y el motivo. Si otro proceso vivo lo tiene, error «hay otro cambio en curso» (409 en el panel). Un candado cuyo proceso murió se retira. Es reentrante dentro del mismo hilo.
2. **Respaldo.** `respaldar()` copia fuera del repo todo lo que el motor puede tocar (`elementos()`: sistemas, INDICE, FLUJO, archivos de agente, `.claude/settings.json`, exclusiones de IA) y escribe `transaccion.json` con `"en_curso": true`.
3. **Cambio.** El bloque hace su trabajo (construir y colocar sistemas de forma atómica, regenerar lo generado).
4. **Cierre o vuelta atrás.** Si el bloque termina, el respaldo pasa a `"en_curso": false` y se podan los antiguos (`respaldos_por_proyecto`, 3 por defecto). Si lanza cualquier excepción, `restaurar()` deja el proyecto exactamente como estaba antes de propagarla.
5. **Corte de luz.** Un respaldo que sigue `"en_curso"` sin nadie con el candado es una transacción interrumpida: `reparar` la restaura.
6. **Deshacer.** `deshacer()` restaura un respaldo dentro de una transacción nueva, así que deshacer también se puede deshacer.

El trabajo de `uxyngraphar/trabajo/` nunca entra en el respaldo: no se toca, salvo las carpetas vacías que creó una transacción fallida.

- **Memorias.** Las memorias del proyecto (`trabajo/<id>/memorias/`) las gestiona `scripts/comun/uxyn_memorias.py` en cada sistema; el panel las lee y decide con `memorias_repo.py` (rutas `/api/repo/memorias…`), actuando como persona.
- **Límites y permisos.** `permisos` del manifiesto es la única fuente: `scripts/comun/uxyn_permisos.py` genera el bloque de `PERMISOS.md` y da `exigir` a los scripts propios; `protecciones.py` traduce `permisos.rutas` a reglas `deny` y exclusiones de IA; `piezas.limites_y_permisos` y `verificar.py` lo validan.

## Pruebas

`motor/pruebas/` cubre el motor, el panel (servidor real en un hilo), el instalador (releases servidas en local) y las pruebas propias de cada sistema (sobre su construcción). Ninguna toca la instalación real: `_rutas.py` fija una carpeta de datos temporal.
