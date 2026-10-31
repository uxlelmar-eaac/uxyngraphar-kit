# Manual oficial de uxyngraphar

**Copyright © 2026 uxleleaac / uxlelmar** · Licencia del kit: [CC BY 4.0](../LICENCIA.md)

Esta carpeta es el **manual público** del kit. Vive **fuera** de `español/` (packs, instalador y `_compartido`): no se instala en `docs/` de los proyectos y no participa en PARIDAD ni en `construir-packs.py`.

## Para quién

| Quién | Empieza aquí |
|-------|----------------|
| Persona (humana) | [INDICE.md](INDICE.md) → [00-inicio/mapa-lectura.md](00-inicio/mapa-lectura.md) |
| Agente de IA | **[AGENTES.md](AGENTES.md)** (única entrada obligatoria) |
| Quién solo quiere instalar ya | [01-instalacion/checklist.md](01-instalacion/checklist.md) |

## Mapa rápido

```text
documentacion/
├── README.md                 ← estás aquí
├── AGENTES.md                ← entrada IA: instalar + configurar + instruir humano
├── INDICE.md                 ← índice completo
├── 00-inicio/                ← qué es, mapa, glosario
├── 01-instalacion/           ← herramienta, sembrar, clon, checklist
├── 02-configuracion/         ← proyecto, config JSON, protecciones, doctor
├── 03-uso-humano/            ← día a día, aprobar, panel, actualizar
├── 04-uso-ia/                ← protocolo, playbook, límites, hablar con humanos
├── 05-comandos/              ← referencia CLI
├── 06-packs/                 ← servidor, cliente, monorepo
├── 07-colaboracion/          ← sugerencias EVO
└── 08-referencia/            ← estructura, enlaces a guías del pack, licencias
```

## Relación con el pack instalado

Tras sembrar el pack, cada proyecto tiene su propia copia en `docs/` con guías operativas (`docs/10-guias/…`). Este manual **explica el kit**; las guías del pack **gobiernan el día a día** dentro del repo. Cuando haya solape, este manual enlaza a la guía canónica del pack (no la duplica al detalle).

## Sitio web

La aplicación frontend publica una lectura navegable en `/documentacion`, alineada con este manual.
