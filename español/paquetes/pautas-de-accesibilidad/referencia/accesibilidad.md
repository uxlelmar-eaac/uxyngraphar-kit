# Accesibilidad mínima (WCAG 2.2 AA)

Cada punto lleva entre paréntesis el código de criterio que se usa en la tabla «Barreras».

- **Contraste** (`contraste`): texto ≥ 4.5:1; texto grande, iconos y bordes de controles ≥ 3:1.
- **Teclado** (`teclado`): todo lo interactivo se alcanza y se usa con teclado; orden lógico; sin trampas de foco.
- **Foco** (`foco`): siempre visible y no tapado por elementos fijos.
- **Objetivos táctiles** (`objetivos`): al menos 24×24 px (mejor 44×44).
- **Semántica** (`semantica`): elementos nativos (`button`, `a`, `label`, encabezados en orden); ARIA solo cuando no hay nativo.
- **Formularios** (`formularios`): etiqueta visible por campo; errores en texto, junto al campo y anunciados; no depender solo del color.
- **Medios** (`medios`): texto alternativo en imágenes informativas; subtítulos en vídeo con voz.
- **Movimiento** (`movimiento`): respetar `prefers-reduced-motion`; nada parpadea más de 3 veces por segundo.
- **Zoom y reflujo** (`zoom`): usable al 200 % y a 320 px de ancho sin desplazamiento horizontal.

Comprobación rápida: Lighthouse/axe + recorrido solo con teclado + lector de pantalla en la tarea principal.

## Gravedad

| Gravedad | Significa | Ejemplo |
|----------|-----------|---------|
| `bloqueante` | impide completar la tarea | el botón de enviar no se alcanza con teclado |
| `grave` | se completa con mucho esfuerzo o con ayuda | errores sin texto, solo en rojo |
| `menor` | molesta, pero se completa | un icono decorativo anunciado por el lector |
