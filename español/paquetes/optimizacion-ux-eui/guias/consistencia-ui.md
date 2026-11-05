# Consistencia de interfaz

## Tokens antes que valores sueltos
- **Color:** usa los tokens del proyecto (primario, superficie, texto, borde, estados éxito/aviso/error). Un hex suelto en un componente es un hallazgo `UI`.
- **Espaciado:** una escala (p. ej. 4 · 8 · 12 · 16 · 24 · 32 · 48). Valores fuera de escala, hallazgo.
- **Tipografía:** una escala de tamaños y pesos; máximo 2 familias.
- **Radios, sombras, bordes:** pocos valores, siempre los mismos.

## Componentes
- Antes de crear uno, busca si existe; si existe pero no encaja, propón extenderlo.
- Un mismo propósito = un mismo componente (no tres botones primarios distintos).

## Estados que todo componente interactivo cubre
normal · hover · foco (visible) · activo · deshabilitado · carga · vacío · error

## Jerarquía y lectura
- Una acción primaria por vista; las secundarias, visualmente subordinadas.
- Alineación a una rejilla; agrupación por proximidad; contraste de tamaño para jerarquía, no solo color.
