# Playbook IA: instalar y configurar por completo

Ejecuta en orden. Tras cada bloque, resume a la persona qué ocurrió. Entrada: [../AGENTES.md](../AGENTES.md).

## A. Preparar

1. Python + git ([../01-instalacion/requisitos.md](../01-instalacion/requisitos.md)). En Windows: `py -3`.
2. Herramienta o clon ([../01-instalacion/herramienta.md](../01-instalacion/herramienta.md)). `uxyngraphar version`.
3. Confirma: rutas, pack, layout (raíz / monorepo / dos repos), `--colaborar no` salvo pedido contrario.

## B. Sembrar

Sigue las recetas de [../01-instalacion/sembrar-proyecto.md](../01-instalacion/sembrar-proyecto.md).  
**Prohibido** inventar flags: [../05-comandos/referencia-cli.md](../05-comandos/referencia-cli.md).

Ejemplo un pack:

```bash
uxyngraphar instalar "$REPO" --pack servidor --si --colaborar no
```

## C. Configurar

1. Inspecciona el árbol real.
2. Rellena plantillas P ([../02-configuracion/configuracion-proyecto.md](../02-configuracion/configuracion-proyecto.md)).
3. Propón config JSON; confirma con humano.
4. No `feedback.py activar|enviar`.

## D. Verificar

```bash
python3 docs/scripts/doctor.py
# monorepo: python3 apps/api/docs/scripts/doctor.py  (etc.)
```

## E. Cerrar

1. Archivos para commit (sin `.env`).
2. [Checklist](../01-instalacion/checklist.md).
3. [Instruir humano](instruir-humano.md). Ante errores: [../01-instalacion/fallos-comunes.md](../01-instalacion/fallos-comunes.md).
