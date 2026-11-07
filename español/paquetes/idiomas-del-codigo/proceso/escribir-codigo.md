---
fase: escribir-codigo
resuelve: [codigo-en-idioma-mezclado]
skills: [consultar-glosario]
---

# Fase: escribir código

## Objetivo

Que todo artefacto que el pedido añade o cambia esté en inglés ASCII desde el primer borrador, con los términos del glosario como única excepción.

## Entradas

- Los problemas heredados y los términos permitidos de `diagnosticar`.
- La guía `referencia/idioma.md`.

## Pasos

1. Escribe en inglés ASCII cada identificador, archivo, carpeta, prueba, log, error para desarrolladores y comentario nuevos.
2. Un concepto de negocio sin traducción precisa: si está en el glosario, úsalo en ASCII y con el casing del código (`expedienteId`); si no, tradúcelo y propón la fila a la persona (skill `consultar-glosario`).
3. Los textos que verá el usuario no se escriben en la lógica: van por i18n con una clave en inglés (`errors.payment.declined`); el servidor devuelve un código estable en inglés.
4. Un campo de contrato externo se refleja tal cual solo en el DTO, esquema o adaptador; pasado el adaptador, nombres en inglés con un mapeo explícito.
5. No renombres código antiguo en otro idioma salvo que sea seguro, haya pruebas y todos sus usos estén dentro de lo que pidió la persona; si es un contrato público, detente (deriva a `decisiones-de-arquitectura`).

## Criterio de salida

- Ningún artefacto nuevo fuera del inglés ASCII, salvo términos del glosario y campos de contratos externos en la frontera.
- Ningún texto para el usuario escrito en la lógica.
