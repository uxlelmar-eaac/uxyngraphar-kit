# Reglas del proyecto y ajustes locales

Activado con «usa el paquete reglas-del-proyecto» / «sigue el protocolo reglas del proyecto» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/reglas-del-proyecto/scripts`.

Dos piezas que los paquetes inmutables no pueden dar solos:
- **Reglas del proyecto** (`RP-*`): convenciones y prohibiciones que el equipo pone a su propio código. Con `comprobacion_prohibido` / `comprobacion_obligatorio` (regex) se verifican sin IA.
- **Ajustes locales** (`AJ-*`): lo que, solo en este proyecto, manda sobre un archivo de otro paquete instalado (por ejemplo, un paso de su README), sin editarlo.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Antes de tocar código: `python3 $S/reglas.py para <archivos o anclas>` y respeta lo que imprima. Para ver todas: `python3 $S/reglas.py indice`.
4. Si no puedes cumplir una regla: `python3 $S/comun/fichas.py nueva excepcion --slug <slug>` (cita `regla`, `archivos` y motivo) y **espera** a que una persona la apruebe.
5. Para proponer una regla o un ajuste local: `fichas.py nueva regla …` / `fichas.py nueva ajuste …`. Nacen `propuesta` / `propuesto`; una persona los activa.
6. Antes de terminar: `python3 $S/comun/verificar.py`, `python3 $S/verificar-reglas.py` y, sobre lo cambiado, `python3 $S/reglas.py comprobar --git`.

Persona: activar una regla `fichas.py estado RP-… activa --humano`; aprobar una excepción `fichas.py estado EX-… aprobada --humano`; activar o revisar un ajuste `reglas.py aprobar-ajuste AJ-… --humano` (guarda la huella del archivo que complementa).

Trabajo: `uxyngraphar/trabajo/reglas-del-proyecto/{reglas,excepciones,ajustes-locales}/`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Las reglas activas se cumplen.** Una `bloqueante` incumplida sin excepción aprobada hace fallar la verificación; una `aviso` solo avisa.
2. **Nunca te saltes una regla en silencio.** O la cumples, o propones una excepción y esperas.
3. **Solo una persona** activa o retira reglas, aprueba o rechaza excepciones y activa, revisa o retira ajustes locales.
4. **No edites una regla, excepción o ajuste activos.** Si hay que cambiarlos, propón uno nuevo (`reemplaza: RP-…`) y que una persona retire el anterior.
5. **Precedencia de los ajustes locales:** un ajuste `activo` manda sobre `aplica_a` de su paquete, solo en este proyecto y solo en lo que dice. Si está «por revisar» (el paquete cambió), síguelo y avisa.
6. **Un ajuste es temporal:** cuando el paquete incorpora el cambio, una persona lo retira (`retirado`), que queda como historia.
7. **Lectura mínima:** por defecto solo `reglas.py indice` o `reglas.py para`; no abras todas las fichas.
