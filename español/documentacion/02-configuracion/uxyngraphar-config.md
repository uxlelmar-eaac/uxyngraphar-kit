# uxyngraphar.config.json

Archivo en `uxyngraphar/uxyngraphar.config.json`. Define comportamiento local del pack (niveles de idioma, feedback, etc.).

## Frases que activan el protocolo

Al final de un pedido escribes **«sigue el protocolo uxyngraphar»** (o `uxyn`, `uxynar`) para que el agente siga el flujo del pack. Puedes cambiar o añadir frases:

```json
{ "protocolo": { "alias": ["uxyngraphar", "uxyn", "uxynar", "del sistema"] } }
```

Con eso vale «sigue el protocolo del sistema». Desde el panel: **Proyecto → Configuración → Cómo se pide el protocolo** (también en la **Plantilla**, para los proyectos nuevos). El agente las lee en la línea «Activación» de `ESTADO.md`. Si editas el archivo a mano, ponla al día con **Proyecto → Salud → «Arreglar»** (o `python3 uxyngraphar/scripts/doctor.py --fix`).

## Fase de preguntas

Por defecto, antes de crear una instrucción el agente aclara el pedido con decisiones en el chat (`activo: true`, topes `rondas: [6, 4, 2]`, `presupuesto_max: 12`). `rondas` es un techo por ronda (no cuota); el impacto del pedido decide cuántas se usan. Puedes apagarlo o cambiar topes y presupuesto:

```json
{ "preguntas": { "activo": true, "rondas": [6, 4, 2], "presupuesto_max": 12 } }
```

Panel: **Proyecto → Configuración → Fase de preguntas**. En un pedido concreto: «salta preguntas». Guía: `uxyngraphar/10-guias/fase-preguntas.md`.

## Cómo editarlo

- **Recomendado:** `uxyngraphar` → **Proyecto → Configuración** (vista previa de cada cambio y copia antes de guardar)
- Consulta en texto (avanzado): `uxyngraphar configuracion [RUTA]`
- A mano solo si sabes el esquema

## Reglas

- Secciones nuevas entran con **default que no cambia comportamiento**.
- Migraciones las aplica el actualizador (`migraciones.py`), no a mano de forma ad hoc.
- Agentes: **no** deben editar este archivo salvo pedido explícito humano; proponer cambios en el chat.

## Guía canónica

`uxyngraphar/10-guias/configuracion-uxyngraphar.md` (en el proyecto instalado).
