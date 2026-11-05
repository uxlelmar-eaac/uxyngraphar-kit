# Accesibilidad mínima (WCAG 2.2 AA)

- **Contraste:** texto ≥ 4.5:1; texto grande, iconos y bordes de controles ≥ 3:1.
- **Teclado:** todo lo interactivo se alcanza y se usa con teclado; orden lógico; sin trampas de foco; foco siempre visible y no tapado por elementos fijos.
- **Objetivos táctiles:** al menos 24×24 px (mejor 44×44).
- **Semántica:** elementos nativos (`button`, `a`, `label`, encabezados en orden); ARIA solo cuando no hay nativo.
- **Formularios:** etiqueta visible por campo; errores en texto, junto al campo y anunciados; no depender solo del color.
- **Medios:** texto alternativo en imágenes informativas; subtítulos en vídeo con voz.
- **Movimiento:** respetar `prefers-reduced-motion`; nada parpadea más de 3 veces por segundo.
- **Zoom y reflujo:** usable al 200 % y a 320 px de ancho sin desplazamiento horizontal.

Comprobación rápida: Lighthouse/axe + recorrido solo con teclado + lector de pantalla en la tarea principal.
