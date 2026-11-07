# Límites

Se cumplen en todo el trabajo del paquete.

1. **Solo lectura:** las revisiones no corrigen nada; reportan. La única que ejecuta es `humo`, y solo con `--ejecutar`.
2. **Bajo pedido:** no se encadenan a commits, CI ni a otras tareas sin que la persona lo pida.
3. **Humo sin efectos reales:** los comandos apuntan a entornos de prueba o modo simulación; nunca a producción.
4. **Hallazgos con evidencia** (`archivo:línea`), en tabla; la prosa solo en recomendaciones.
5. **Un hallazgo no es una corrección:** cada uno se resuelve por su propio flujo y con la aprobación que corresponda.
6. **No cambies los ajustes** (`humo`, `prefijo_global`, `dias_manual`, `raices`…) para que una revisión salga limpia: son de la persona.

## Cuándo detenerse y preguntar

- Un comando de `humo` parece apuntar a producción o tener efectos reales (envía correos, cobra, borra datos): no lo ejecutes.
- Una revisión da cientos de hallazgos del mismo tipo: probablemente falta un ajuste (`prefijo_global`, `excluir`); pregunta antes de informar.
- Un hallazgo exige decidir si el código o la ficha están mal: esa decisión es de la persona.
- La persona pide corregir los hallazgos en la misma tarea: eso es otro flujo (instrucción aprobada).
