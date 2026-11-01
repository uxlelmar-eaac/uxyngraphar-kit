# uxyngraphar.config.json

Archivo en `docs/uxyngraphar.config.json`. Define comportamiento local del pack (niveles de idioma, feedback, etc.).

## Frases que activan el protocolo

Al final de un pedido escribes **«sigue el protocolo uxyngraphar»** (o `uxyn`, `uxynar`) para que el agente siga el flujo del pack. Puedes cambiar o añadir frases:

```json
{ "protocolo": { "alias": ["uxyngraphar", "uxyn", "uxynar", "del sistema"] } }
```

Con eso vale «sigue el protocolo del sistema». Desde el panel: **Configuración del proyecto → Cómo se pide el protocolo** (también en la **Plantilla**, para los proyectos nuevos). El agente las lee en la línea «Activación» de `ESTADO.md`. Si editas el archivo a mano, ponla al día con `python3 docs/scripts/doctor.py --fix`.

## Cómo editarlo

- **Recomendado:** `uxyngraphar panel` → configuración del proyecto
- Consulta: `uxyngraphar configuracion [RUTA]`
- A mano solo si sabes el esquema

## Reglas

- Secciones nuevas entran con **default que no cambia comportamiento**.
- Migraciones las aplica el actualizador (`migraciones.py`), no a mano de forma ad hoc.
- Agentes: **no** deben editar este archivo salvo pedido explícito humano; proponer cambios en el chat.

## Guía canónica

`docs/10-guias/configuracion-uxyngraphar.md` (en el proyecto instalado).
