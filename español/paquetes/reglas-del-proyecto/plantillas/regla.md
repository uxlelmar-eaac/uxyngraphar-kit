---
id: {{id}}
status: {{status}}
fecha: {{fecha}}
titulo: {{titulo}}
nivel: bloqueante
aplica_a:
  - src/**/*.ts
resumen: Una línea que el agente pueda cumplir sin leer más.
comprobacion_prohibido: ""
comprobacion_obligatorio: ""
reemplaza: null
---
<!-- nivel: bloqueante | aviso.
     comprobacion_prohibido: regex que no debe aparecer en ninguna línea de los archivos de aplica_a (vacío = sin comprobación).
     comprobacion_obligatorio: regex que debe aparecer en cada archivo de aplica_a (vacío = sin comprobación).
     Las regex no pueden contener « #» (espacio + almohadilla): el frontmatter lo toma como comentario.
     Sin comprobación, la regla vale como instrucción para el agente y para la revisión humana. -->

# {{titulo}}

**Regla:** qué se hace o no se hace (1–2 frases).

**Porqué:** el motivo (1 frase).

**Ejemplo:** `correcto` en vez de `incorrecto`.
