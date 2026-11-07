---
name: sustituir-por-variable-de-entorno
description: Sustituye un valor sensible del código por la lectura de una variable de entorno (o un placeholder) y la documenta sin valor en la plantilla .env.example.
resuelve: [secretos-en-el-codigo, archivos-de-secretos-versionados]
---

# Sustituir por variable de entorno

## Cuándo usarla

- El código necesita una credencial (clave de API, contraseña de base de datos, token).
- `secretos.py` marca un hallazgo en un archivo que tú escribiste.

## Pasos

1. Nombra la variable en `UPPER_SNAKE_CASE` y con el servicio delante (`STRIPE_SECRET_KEY`, `DATABASE_URL`).
2. Léela con el mecanismo del proyecto (`process.env.STRIPE_SECRET_KEY`, `os.environ["STRIPE_SECRET_KEY"]`, el módulo de configuración si existe) y falla con un mensaje claro si falta; no pongas un valor por defecto real.
3. En documentación y ejemplos, escribe `<STRIPE_SECRET_KEY>` en lugar del valor.
4. Añade la variable a la plantilla `.env.example` (o `.sample`, `.template`) con valor vacío o placeholder. Nunca edites ni crees `.env`.
5. Si había un archivo de secretos en el repositorio y es tuyo, conviértelo en plantilla sin valores y comprueba que `.gitignore` excluye el real; si no es tuyo, avisa.
6. Vuelve a escanear las rutas tocadas.

## Resultado

- El código lee la credencial del entorno, la plantilla la documenta sin valor y `secretos.py` ya no marca la línea.
