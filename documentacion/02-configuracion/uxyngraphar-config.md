# uxyngraphar.config.json

Archivo en `docs/uxyngraphar.config.json`. Define comportamiento local del pack (niveles de idioma, feedback, etc.).

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
