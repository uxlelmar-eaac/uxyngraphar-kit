# 0010 · Límites y permisos en el núcleo obligatorio de cada sistema

- **Estado:** aceptada
- **Fecha:** 2026-11-11

## Contexto

Lo que el agente puede hacer solo y lo que decide una persona tiende a repartirse: unos límites opcionales que muchos
sistemas no traen, rutas que la IA no escribe o no lee en campos sueltos del manifiesto, los status de la persona en
`fichas.<tipo>.solo_humano` y las acciones de memorias en el código de `uxyn_memorias.py`. Hace falta un sitio único
donde el agente lea sus permisos y una forma de declarar que un script propio del sistema es solo de una persona.

## Decisión

1. **Núcleo:** todo sistema lleva `LIMITES.md` (`# Límites`, reglas numeradas y «Cuándo detenerse y preguntar») y
   `PERMISOS.md` (`# Permisos` con un bloque generado). `limites` no es una pieza.
2. **Manifiesto:** el campo obligatorio `permisos` `{rutas: {protegidas, fuera_de_ia}, acciones: {agente, solo_persona}}`
   es la única fuente: el bloque de `PERMISOS.md`, las reglas `deny`, las exclusiones de IA y el paso del README salen
   de él. Las acciones de memorias y los `solo_humano` de las fichas entran de
   forma implícita.
3. **Aplicación:** `scripts/comun/uxyn_permisos.py` da `exigir(sistema, accion)` para los scripts propios (falla si no lo
   ejecuta una persona). El validador y `verificar.py` exigen los dos archivos, el bloque al día y que los scripts citados
   existan; avisan de un script con acciones de la persona que nunca llama a `exigir`.
4. **Activación:** el bloque de entrada lleva siempre el paso «Límites y permisos», justo después de las memorias, y el
   bloque de AGENTES/CLAUDE recuerda que las acciones de «Solo una persona» no las ejecuta el agente.

## Consecuencias

- Los sistemas del catálogo del servidor deben publicarse con `LIMITES.md`, `PERMISOS.md` y `permisos`; los que no los
  traigan no se construyen.
- `uxyngraphar pieza <id> agregar|quitar limites` falla con un mensaje claro; el generador siempre escribe `LIMITES.md`
  (texto genérico y un aviso si la especificación no trae `limites`) y acepta `permisos`.
- El freno sigue siendo cooperativo: `exigir` y las reglas `deny` paran a un agente que sigue las instrucciones y las
  formas directas, no a quien se salta el protocolo a propósito.
