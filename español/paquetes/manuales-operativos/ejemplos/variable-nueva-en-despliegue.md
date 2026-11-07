# Caso: una variable de entorno nueva cambia el despliegue

## Pedido

«Añade el envío de correos con el proveedor de email; la clave va en una variable de entorno.» Existe el manual `MAN-20260402-desplegar-api` (`vigente`).

## Recorrido

**localizar-manual.** `fichas.py listar manual --status vigente` muestra `desplegar-api` y `restaurar-base-de-datos`. El cambio añade una variable obligatoria al arranque: afecta a `desplegar-api` (requisitos y verificación). `restaurar-base-de-datos` no cambia.

**redactar-pasos → actualizar-manual** (skill). Cambios en el manual:

```markdown
## Requisitos
- Variables: `<EMAIL_API_KEY>` (gestor de secretos del equipo, entrada «email/produccion»)

## Pasos
3. `fly secrets set EMAIL_API_KEY=<EMAIL_API_KEY> -a tienda-api` → «Secrets are staged for the first deployment»
4. `fly deploy -a tienda-api` → «v42 deployed successfully»

## Verificación
`curl -s https://api.tienda.example/health` → `{"status":"ok","email":"ok"}`

## Cómo revertir
`fly releases rollback -a tienda-api` → vuelve a la versión anterior; la variable puede quedarse (no la lee).
```

Ningún valor real de la clave: solo el nombre y su origen.

**entregar-para-verificacion.**

```
python3 $P/scripts/comun/fichas.py estado MAN-20260402-desplegar-api borrador
python3 $P/scripts/comun/verificar.py
```

Al cerrar: «`desplegar-api` vuelve a borrador; pruébalo en el próximo despliegue y márcalo con `fichas.py estado MAN-20260402-desplegar-api vigente --humano` y `ultima_verificacion`».

## Resultado

- Manual de despliegue con la variable nueva, un paso que la configura, su verificación y su reversión.
- En `borrador` hasta que la persona lo prueba.
