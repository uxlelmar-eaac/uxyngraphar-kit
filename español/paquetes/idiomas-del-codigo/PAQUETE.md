# Idiomas del código

Mantiene un solo idioma en todo artefacto de código: inglés ASCII, salvo los términos de dominio que una persona aprueba en el glosario del proyecto, y el texto para el usuario fuera de la lógica, por i18n. Los nombres de archivo se comprueban sin IA con `idiomas.py`.

## Qué resuelve

El idioma se mezcla según quién escribió cada parte: un `calcularTotal` junto a un `applyDiscount`, archivos `cupón.ts`, logs en tres idiomas y mensajes para el usuario escritos en la lógica. Este paquete fija la regla (artefactos en inglés ASCII, conversación en el idioma de la persona), el único hueco permitido (el glosario de términos de dominio, que decide una persona) y cómo tratar el código antiguo en otro idioma sin renombrarlo de paso.

## Problemas que cubre

- `codigo-en-idioma-mezclado`: código, nombres de archivo o textos para desarrolladores fuera del inglés ASCII sin que el término esté en el glosario.

## Fuera de alcance

- Que los nombres digan qué es cada cosa (genéricos, unidades, casing del lenguaje) y el límite de líneas: `calidad-de-codigo`.
- Idioma y formato de los mensajes de commit y de los nombres de rama: `mensajes-de-commit`.
- Renombrar contratos públicos (rutas de API, columnas, eventos) escritos en otro idioma: `decisiones-de-arquitectura` (ADR y migración con convivencia).
- Traducir el texto para el usuario final y mantener los archivos de locale: no lo cubre el kit; este paquete solo exige que ese texto vaya por i18n.

## Cuándo usarlo

- En cualquier tarea que escriba o modifique código del proyecto, sobre todo si el pedido, el ticket o el código antiguo están en otro idioma.
- Al modelar conceptos de negocio sin traducción precisa al inglés o al reflejar un contrato externo (facturación electrónica, pasarela de pago).
- Al adoptar el paquete en un proyecto existente (diagnóstico con `idiomas.py` sobre todas las `raices`).

## Cuándo no usarlo

- En archivos generados, vendorizados o migraciones ya aplicadas (van en `excluir`).
- Para redactar la documentación de `uxyngraphar/`: va en el idioma del equipo.

## Entradas y salidas

- Entradas: el código bajo `raices`, los ajustes en `uxyngraphar/trabajo/idiomas-del-codigo/ajustes.json` y el glosario `uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md` (protegido: lo edita solo una persona).
- Salidas: código con todo artefacto nuevo en inglés ASCII, propuestas de términos para el glosario (nunca escritas por el agente) y el informe de `idiomas.py` (`archivo: motivo` y un resumen con el número de problemas).

## Paquetes complementarios

- `calidad-de-codigo`: que los nombres en inglés además se expliquen solos y quepan en archivos cortos.
- `mensajes-de-commit`: el idioma y el formato de los commits con los que se entrega el cambio.
- `decisiones-de-arquitectura`: la ADR para renombrar un contrato público escrito en otro idioma.
- `contratos-entre-repositorios`: los términos del glosario que viajan en un contrato de API se escriben igual en todos los repositorios.
