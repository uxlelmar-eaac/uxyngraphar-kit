# Componentes

Las piezas que define el paquete.

## Archivo histórico

`uxyngraphar/trabajo/documentos-archivados/archivo/<AAAA-MM-DD>/<nombre>`: copias de documentos retirados, agrupadas por la fecha en que se archivaron. Solo crece: nada se edita ni se borra. Está en `fuera_de_ia` (el agente no lo lee: `.cursorignore` y equivalentes) y en `protegidos` (el agente no lo edita: reglas `deny`).

## Documento retirado

Archivo del proyecto que deja de usarse. Se archiva por copia (conservando fechas) y el original queda donde estaba hasta que la persona decida borrarlo. No se archivan archivos de `uxyngraphar/paquetes/`.

## Aviso de retirada

Plantilla `plantillas/aviso-de-retirada.md`: texto breve que puede ocupar el lugar del original cuando la persona prefiere dejar una referencia en vez de borrarlo. Dice cuándo se retiró, dónde está la copia, el motivo y qué lo sustituye; no copia nada del contenido archivado. Se rellenan a mano el título, la fecha (la de la carpeta del archivo) y el nombre del archivo copiado.

## Acción de la persona

Archivar y consultar el archivo exigen `--humano` y además una terminal interactiva o `UXYNGRAPHAR_HUMANO=1` (nunca con `CI`); el agente no tiene ninguna de las dos. Cuando hacen falta, el agente prepara el comando y se lo da a la persona.
