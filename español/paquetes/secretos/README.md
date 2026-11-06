# Secretos y credenciales — entrada

Activado con «usa el paquete secretos» / «sigue el protocolo secretos» o por `uxyngraphar-work/FLUJO.json`. Rutas relativas a la raíz de la app.

1. Integridad: `python3 uxyngraphar/secretos/scripts/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/secretos/REGLAS.md` y cúmplelas durante toda la tarea.
3. Antes de terminar (y antes de proponer un commit): `python3 uxyngraphar/secretos/scripts/escanear.py`.
   - `--git` escanea solo lo que git versiona o tiene preparado; `--informe` guarda el resultado en `uxyngraphar-work/secretos/informes/`.
   - Código 1 = hay hallazgos: corrige **tu** cambio (sustituye por `<PLACEHOLDER>` o variable de entorno). Si el hallazgo no es tuyo, avisa a la persona; no lo borres ni lo muevas.
4. Qué hacer si aparece un secreto real: `uxyngraphar/secretos/guias/si-aparece-un-secreto.md`.

Ajustes del proyecto (los edita una persona): `uxyngraphar-work/secretos/ajustes.json` con `raices`, `excluir`, `permitir` (globs de rutas exentas) y `max_kb`.
