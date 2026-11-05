# Ciclo de instrucciones — entrada

Activado con «usa el paquete ciclo-instrucciones» / «sigue el protocolo uxyngraphar» (frases en el manifiesto) o por `uxyngraphar-work/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/ciclo-instrucciones/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/ciclo-instrucciones/REGLAS.md`.
3. **Preguntas** (si `ajustes.preguntas` es true y el pedido no dice «salta preguntas»): decide en el chat con la persona y registra `python3 $S/fichas.py nueva pregunta --slug <slug>`. Guía: `guias/preguntas.md`.
4. **Instrucción**: `python3 $S/fichas.py nueva instruccion --slug <slug> --titulo "…"`; rellena alcance, `anclas_codigo` y criterios. **Espera** a que una persona la apruebe (`python3 $S/ciclo.py aprobar <id> --humano`). Sin `approved` no edites código ni documentación.
5. **Contexto**: `python3 $S/ciclo.py contexto <id>` imprime ficha, lectura mínima y anclas con rango. No abras nada más.
6. **Implementa** solo dentro de `anclas_codigo`. Deuda o bugs fuera de alcance: anótalos en la sección «Fuera de alcance» de la instrucción; no los implementes.
7. **Cierre**: `python3 $S/ciclo.py cerrar <id>` y luego `python3 $S/verificar-ciclo.py`.

Trabajo: `uxyngraphar-work/ciclo-instrucciones/{instrucciones,preguntas}/<estado>/`. Ajustes (persona): `uxyngraphar-work/ciclo-instrucciones/ajustes.json`.
