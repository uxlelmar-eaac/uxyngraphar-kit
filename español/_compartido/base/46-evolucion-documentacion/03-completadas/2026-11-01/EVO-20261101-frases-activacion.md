---
id: EVO-20261101-frases-activacion
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - AGENTES.md
  - ESTADO.md
  - 10-guias/configuracion-uxyngraphar.md
  - scripts/control/uxyngraphar_config.py
  - scripts/contexto.py
  - scripts/nucleo/doctor.py
  - scripts/nucleo/flujo.py
proposed_at: 2026-11-01
instruction_derivada: solicitud-humana-20261101-frases-activacion
---
# EVO-20261101 — Frases que activan el protocolo

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita (uxlelmar, 2026-11-01): «De trabajar el flujo habitual es doy la instrucción a la gente y después finalizo con sigue el protocolo de UXINGRAPAR. Entonces me gustaría hacer que esto sea más cómodo, poder configurar cómo la gente va a entender qué protocolo debe seguir. Por ejemplo, que las personas o los usuarios puedan decir en vez de UXINGRAPAR, que siga el protocolo del sistema, que siga el protocolo tal, o por defecto que siga el protocolo uxyn o uxynar.»

## Qué faltaba

La frase «sigue el protocolo uxyngraphar» era una costumbre: no estaba escrita en ningún sitio del pack. El agente seguía el flujo porque `CLAUDE.md`/`AGENTS.md` lo mandan a `AGENTES.md`, no porque reconociera la frase, y no había forma de usar otra (más corta, dictada, o propia del equipo).

## Decisión

- Nueva sección `protocolo.alias` en `uxyngraphar.config.json` (por defecto `uxyngraphar`, `uxyn`, `uxynar`), validada: lista no vacía, frases de 1 a 40 caracteres, sin repetir.
- `AGENTES.md` dice, en una línea, que un pedido que termina en «sigue el protocolo <frase>» pide su flujo, con las frases por defecto y dónde están las del proyecto.
- El agente no lee la configuración al empezar (está fuera de su alcance): las frases del proyecto se escriben en una línea marcada de `ESTADO.md` («Activación»), que ya lee al empezar. Se pone al día al instalar, al guardar desde el panel, con `decisiones.py estado --escribir` y con `doctor.py --fix`; el doctor avisa si quedó desfasada. `contexto.py --activacion` la imprime.
- Panel: campo «Frases para activar el protocolo» en Configuración del proyecto y en la Plantilla (proyectos nuevos).
- Sin cambios en el texto de las reglas R-xx. Coste de arranque: una línea en `AGENTES.md` y tres en `ESTADO.md` (dentro de `ARRANQUE_MAX`).
