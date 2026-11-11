# Guía para diseñar sistemas

Cómo pensar un sistema antes de escribirlo. El contrato (qué valida el motor) está en [`ESPECIFICACION.md`](ESPECIFICACION.md); los nombres, en [`NOMENCLATURA.md`](NOMENCLATURA.md). Esta guía es criterio de diseño: el validador solo avisa, la decisión es del autor.

Para escribirlo, el generador ([`GENERADOR.md`](GENERADOR.md)) lo crea completo desde una especificación o guía su creación paso a paso; los agentes de IA siguen [`GUIA-PARA-AGENTES.md`](GUIA-PARA-AGENTES.md).

## 1. Un sistema es un entorno de trabajo completo

Quien active el sistema en cualquier proyecto debe poder trabajar **solo con su carpeta**: qué problema resuelve, qué no, qué reglas no se rompen, en qué orden se trabaja, qué acciones concretas hay, qué herramientas existen y cómo se ve un caso resuelto. Si para usarlo hace falta leer otro sistema, la frontera está mal puesta o falta una entrada en «Sistemas complementarios».

## 2. Especializado, no generalista

Un sistema atiende **un conjunto acotado de problemas o de acciones** relacionados. La prueba de especialización:

1. **¿Cabe en una frase sin «y además»?** «Mantiene las capas de un monolito modular» sí; «calidad, nombres, commits y glosario» no.
2. **¿Sus problemas comparten proceso?** Si dos problemas necesitan fases distintas, son dos sistemas.
3. **¿Tiene un solo perfil de trabajo?** Si unas reglas se aplican al escribir código y otras al redactar commits, o unas en el servidor y otras en el diseño visual, son perfiles distintos.
4. **¿Pasa de 5 problemas?** El validador avisa: casi siempre es un sistema generalista.
5. **¿Se quitaría entero de un proyecto?** Si un equipo querría quedarse con la mitad, esa mitad es otro sistema.

Cuando un sistema no pasa la prueba, se divide. Los nuevos ids siguen `NOMENCLATURA.md` y la división se anota en el `CHANGELOG.md` de cada uno.

## 3. Elegir las piezas

Solo el núcleo es obligatorio (`sistema.json`, `README.md`, `SISTEMA.md`, `MEMORIAS.md`, `LIMITES.md`, `PERMISOS.md`). `MEMORIAS.md` dice qué
conviene que el agente y la persona recuerden del proyecto al trabajar con el sistema (y qué no): las memorias en sí viven
en `uxyngraphar/trabajo/<id>/memorias/`, las propone el agente y las aprueba la persona (ESPECIFICACION §2.3). `LIMITES.md` y `PERMISOS.md` dicen qué no se
negocia y qué decide solo una persona (ESPECIFICACION §2.4). Las piezas se eligen por lo que el sistema necesita:

| Si el sistema… | Usa |
|----------------|-----|
| se trabaja en pasos con un orden | `proceso` |
| tiene acciones concretas y repetibles | `skills` |
| define conceptos que hay que entender antes de actuar | `componentes` |
| trae scripts | `herramientas` |
| crea estructura en el proyecto | `andamiaje` |
| registra trabajo en fichas o copia documentos al trabajo | `plantillas` |
| tiene conocimiento de consulta largo | `referencia` |
| es fácil de malinterpretar | `ejemplos` |
| tiene scripts con lógica propia | `pruebas` |
| siempre | `cambios` |

`uxyngraphar validar --completitud` dice qué piezas se recomiendan para la familia del sistema. Lo que no encaje en ninguna pieza va como **extensión** declarada.

## 4. Escribir cada pieza

- **`SISTEMA.md`** se escribe primero: si no se pueden escribir sus problemas y su «Fuera de alcance» en pocas líneas, el sistema aún no está pensado.
- **Problemas** (`alcance.problemas`): describen el síntoma, no la solución (`capas-mal-importadas`, no `revisar-capas`).
- **Fuera de alcance:** cada tema dice a qué sistema se deriva (`derivar_a`), o `null` si el kit no lo cubre. Es lo que evita que el sistema crezca hacia lo generalista.
- **Límites** (`LIMITES.md`, núcleo): pocos, comprobables y sin excepciones implícitas. Termina con cuándo detenerse a preguntar.
- **Permisos** (`permisos` del manifiesto): toda acción irreversible o que compromete al proyecto (publicar, aprobar, borrar) va a `solo_persona` y su script llama a `uxyn_permisos.exigir`; lo que el agente no debe escribir, a `rutas.protegidas`; lo que no debe leer, a `rutas.fuera_de_ia`.
- **Fases:** cada una tiene un criterio de salida verificable. Una fase condicional lo dice al principio («Solo si…»).
- **Skills:** una acción por skill, con su comando o archivo exacto. Cada skill dice qué problema resuelve (`resuelve`).
- **Ejemplos:** un pedido real recorrido fase a fase, con los comandos y su salida.
- **README:** el bloque de entrada lo genera el motor; debajo, lo propio del sistema en pocas líneas (qué decide la persona, ajustes).

## 5. Mantener

- Agregar una pieza: `uxyngraphar pieza <id> agregar <pieza>`, rellenar sus marcadores, subir versión MENOR.
- Quitar una pieza: `uxyngraphar pieza <id> quitar <pieza>`, subir versión MAYOR si cambia lo que el sistema garantiza.
- Tras editar el manifiesto: `uxyngraphar indice-sistema <id>` (el panel lo hace al guardar).
- Antes de publicar: `uxyngraphar validar <id>` sin errores y las pruebas del sistema en verde.

El sistema de referencia es `arquitectura-monolitica-por-capas` (en el servidor: `uxyngraphar info arquitectura-monolitica-por-capas`): usa todas las piezas estándar.
