# Caso: una especificación que se retira

## Pedido

«Ya no usamos `docs/especificacion-cobros-v1.md`; guárdalo en el histórico. Lo único que quiero seguir teniendo a mano es que los cobros salen a 60 días.»

**archivar-documento → preparar-archivado** (skill). El archivo existe y no es de un paquete. El dato que la persona quiere a mano no se queda en el archivo (el agente no lo lee): se propone guardarlo como nota con `notas-de-memoria` antes de archivar.

Respuesta a la persona:

```
python3 uxyngraphar/paquetes/documentos-archivados/scripts/archivo.py archivar docs/especificacion-cobros-v1.md --humano
```

«Lo copiará a `uxyngraphar/trabajo/documentos-archivados/archivo/<fecha>/especificacion-cobros-v1.md`; el original sigue en su sitio. Cuando confirmes que está copiado, lo borro si quieres.»

La persona lo ejecuta:

```
$ python3 uxyngraphar/paquetes/documentos-archivados/scripts/archivo.py archivar docs/especificacion-cobros-v1.md --humano
/ruta/a/la/app/uxyngraphar/trabajo/documentos-archivados/archivo/2026-11-06/especificacion-cobros-v1.md
```

Confirma; el agente borra `docs/especificacion-cobros-v1.md` y ejecuta `python3 $P/scripts/comun/verificar.py`.

## Otro día

«¿Qué decía la especificación v1 sobre recargos?» Solo está en el archivo: el agente no lo abre. Pide a la persona que lo consulte:

```
python3 uxyngraphar/paquetes/documentos-archivados/scripts/archivo.py buscar recargo --humano
```

y, si el dato vuelve a importar, que lo traiga como nota de memoria.

## Resultado

- Documento archivado por la persona, con copia fechada; el original, borrado solo tras confirmarlo.
- El agente no leyó ni escribió en `archivo/`.
