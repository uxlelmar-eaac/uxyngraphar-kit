# Guía para diseñar paquetes

Cómo pensar un paquete antes de escribirlo. El contrato (qué valida el motor) está en [`ESPECIFICACION.md`](ESPECIFICACION.md); los nombres, en [`NOMENCLATURA.md`](NOMENCLATURA.md). Esta guía es criterio de diseño: el validador solo avisa, la decisión es del autor.

## 1. Un paquete es un entorno de trabajo completo

Quien active el paquete en cualquier proyecto debe poder trabajar **solo con su carpeta**: qué problema resuelve, qué no, qué reglas no se rompen, en qué orden se trabaja, qué acciones concretas hay, qué herramientas existen y cómo se ve un caso resuelto. Si para usarlo hace falta leer otro paquete, la frontera está mal puesta o falta una entrada en «Paquetes complementarios».

## 2. Especializado, no generalista

Un paquete atiende **un conjunto acotado de problemas o de acciones** relacionados. La prueba de especialización:

1. **¿Cabe en una frase sin «y además»?** «Mantiene las capas de un monolito modular» sí; «calidad, nombres, commits y glosario» no.
2. **¿Sus problemas comparten proceso?** Si dos problemas necesitan fases distintas, son dos paquetes.
3. **¿Tiene un solo perfil de trabajo?** Si unas reglas se aplican al escribir código y otras al redactar commits, o unas en el servidor y otras en el diseño visual, son perfiles distintos.
4. **¿Pasa de 5 problemas?** El validador avisa: casi siempre es un paquete generalista.
5. **¿Se quitaría entero de un proyecto?** Si un equipo querría quedarse con la mitad, esa mitad es otro paquete.

Cuando un paquete no pasa la prueba, se divide. Los nuevos ids siguen `NOMENCLATURA.md` y la división se anota en el `CHANGELOG.md` de cada uno (y en `migracion/migrar.py` si cambia un destino de 1.x).

## 3. Elegir las piezas

Solo el núcleo es obligatorio (`paquete.json`, `README.md`, `PAQUETE.md`). Las piezas se eligen por lo que el paquete necesita:

| Si el paquete… | Usa |
|----------------|-----|
| tiene reglas que no se negocian | `limites` |
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

`uxyngraphar validar --completitud` dice qué piezas se recomiendan para la familia del paquete. Lo que no encaje en ninguna pieza va como **extensión** declarada.

## 4. Escribir cada pieza

- **`PAQUETE.md`** se escribe primero: si no se pueden escribir sus problemas y su «Fuera de alcance» en pocas líneas, el paquete aún no está pensado.
- **Problemas** (`alcance.problemas`): describen el síntoma, no la solución (`capas-mal-importadas`, no `revisar-capas`).
- **Fuera de alcance:** cada tema dice a qué paquete se deriva (`derivar_a`), o `null` si el kit no lo cubre. Es lo que evita que el paquete crezca hacia lo generalista.
- **Límites:** pocos, comprobables y sin excepciones implícitas. Termina con cuándo detenerse a preguntar.
- **Fases:** cada una tiene un criterio de salida verificable. Una fase condicional lo dice al principio («Solo si…»).
- **Skills:** una acción por skill, con su comando o archivo exacto. Cada skill dice qué problema resuelve (`resuelve`).
- **Ejemplos:** un pedido real recorrido fase a fase, con los comandos y su salida.
- **README:** el bloque de entrada lo genera el motor; debajo, lo propio del paquete en pocas líneas (qué decide la persona, ajustes).

## 5. Mantener

- Agregar una pieza: `uxyngraphar pieza <id> agregar <pieza>`, rellenar sus marcadores, subir versión MENOR.
- Quitar una pieza: `uxyngraphar pieza <id> quitar <pieza>`, subir versión MAYOR si cambia lo que el paquete garantiza.
- Tras editar el manifiesto: `uxyngraphar indice-paquete <id>` (el panel lo hace al guardar).
- Antes de publicar: `uxyngraphar validar <id>` sin errores y las pruebas del paquete en verde.

El paquete de referencia es [`arquitectura-monolitica-por-capas`](../paquetes/arquitectura-monolitica-por-capas/PAQUETE.md): usa todas las piezas estándar.
