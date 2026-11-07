# Límites

Se cumplen en todo el código que el agente escribe o modifica. Solo una persona puede cambiar los ajustes o el glosario.

1. **Artefactos en inglés ASCII.** Código, identificadores, nombres de archivo y carpeta, pruebas, logs, errores para desarrolladores, comentarios y títulos de PR van en inglés y ASCII, aunque el pedido o el código antiguo estén en otro idioma. La conversación va en el idioma de la persona.
2. **Texto para el usuario por i18n.** Nunca se escribe en la lógica: va a los archivos de locale con una clave en inglés (`errors.payment.declined`); el servidor devuelve un código estable en inglés.
3. **Glosario.** Un término de dominio en otro idioma solo si está en `GLOSARIO.md`, en ASCII, con el casing del código y sin conjugar ni pluralizar en su idioma. El agente no edita el glosario (está en «protegidos»): propone la fila a la persona y, mientras tanto, traduce.
4. **Contratos externos en la frontera.** Un campo de un contrato que no controlamos se refleja tal cual solo en el DTO, esquema o adaptador; pasado el adaptador, nombres en inglés con un mapeo explícito.
5. **Código antiguo.** El código en otro idioma no se renombra de paso: solo si es seguro, hay pruebas y todos sus usos están dentro de lo que pidió la persona. Los contratos públicos nunca se renombran de paso.
6. **No se debilita la revisión.** El agente no edita `ajustes.json` ni añade exclusiones para que `idiomas.py` pase.

## Cuándo detenerse y preguntar

- Un término de negocio no tiene traducción precisa y no está en el glosario: propón que una persona lo añada.
- El código que rodea al cambio está en otro idioma y renombrarlo no es seguro dentro de la tarea.
- El cambio exige renombrar un contrato público (ruta de API, columna, evento persistido) escrito en otro idioma: deriva a `decisiones-de-arquitectura`.
- `idiomas.py` marca archivos generados o de terceros que no están en `excluir`: la persona decide si excluirlos.
