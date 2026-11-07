# Caso: regenerar el cliente de la API con una herramienta autorizada

## Pedido

«Regenera el cliente de la API, que el backend añadió el endpoint de facturas.» El proyecto tiene una herramienta autorizada para eso.

## Recorrido

**buscar-herramienta.**

```
python3 $P/scripts/comun/fichas.py listar autorizada --status authorized
HER-20261001-generar-cliente-api	authorized	Regenerar el cliente de la API desde openapi.json
```

Ficha (resumida):

```yaml
id: HER-20261001-generar-cliente-api
status: authorized
source: human
authorized_by: "Ana (equipo API)"
authorized_at: 2026-10-01
anclas_codigo:
  - scripts/generar-cliente.sh
  - src/api/generated/
```

- Cómo ejecutarla: 1. `sh scripts/generar-cliente.sh` → escribe `src/api/generated/`; 2. `npx tsc --noEmit` → sin errores.
- Alcance permitido: regenerar el cliente cuando cambia `openapi.json` del backend, sin tocar el código que lo usa.
- No usar si: hay que adaptar llamadas existentes a un cambio incompatible.

**comprobar-encaje-de-pedido** (skill): el pedido es regenerar por un endpoint nuevo; no pide adaptar llamadas. Encaja en «regenerar el cliente cuando cambia `openapi.json`».

**ejecutar-herramienta.**

```
python3 $P/scripts/verificar-herramientas.py
herramientas: 0 errores, 0 avisos
sh scripts/generar-cliente.sh
npx tsc --noEmit
```

Solo cambió `src/api/generated/` (dentro de las anclas). Informe a la persona: «Usé `HER-20261001-generar-cliente-api`; aparece `FacturasApi` en `src/api/generated/`; `tsc` sin errores».

## Variante: el pedido no encaja

«Regenera el cliente y cambia la pantalla de pedidos para que use el nuevo campo `total_con_iva`.» La segunda parte adapta código existente: la herramienta no la cubre. Se pregunta a la persona si limitar el pedido a regenerar (herramienta) o seguir el proceso normal para todo (instrucción).

## Variante: proponer una herramienta

La persona ha pedido cuatro veces en un mes «actualiza las traducciones desde la hoja compartida» y no hay herramienta. Tras resolver el pedido de hoy por el proceso normal, **proponer-herramienta**:

```
python3 $P/scripts/comun/fichas.py nueva propuesta --slug actualizar-traducciones --titulo "Actualizar traducciones desde la hoja compartida"
uxyngraphar/trabajo/herramientas-autorizadas/propuestas/pendientes/PRO-20261106-actualizar-traducciones.md
```

Skill `redactar-propuesta`: motivo «pedido 4 veces en octubre», solución `node scripts/sync-i18n.mjs`, anclas `scripts/sync-i18n.mjs` y `src/i18n/*.json`, alcance «solo cuando cambia la hoja; no añadir idiomas nuevos». Después:

```
python3 $P/scripts/comun/fichas.py estado PRO-20261106-actualizar-traducciones en-evaluacion
```

Si el agente intentara promoverla él mismo:

```
python3 $P/scripts/comun/fichas.py estado PRO-20261106-actualizar-traducciones promovida
error: «promovida» solo lo asigna una persona (usa --humano si eres tú)
```

## Resultado

- El pedido que encaja se resuelve sin instrucción nueva, solo en las anclas de la herramienta.
- El procedimiento repetido queda propuesto para que la persona decida; hasta entonces, no se usa como herramienta.
