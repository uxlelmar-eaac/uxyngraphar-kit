---
name: completar-estados-de-interfaz
description: Rellena «Estados de UI» de una ficha de página con lo que ve el usuario en carga, vacío, error y éxito, leído del código o preguntado a la persona.
resuelve: [estados-de-interfaz-sin-definir, fichas-de-pagina-desfasadas]
---

# Completar estados de interfaz

## Cuándo usarla

- Al documentar una página nueva.
- Cuando el cambio toca la carga de datos, el manejo de errores o lo que se muestra sin resultados.

## Pasos

1. Localiza en el código cómo se resuelve cada estado: indicador de carga o `loading`, rama sin datos, captura de errores o `error boundary`, y la vista con datos.
2. Escribe una línea por estado diciendo **qué ve el usuario**, no cómo se implementa:
   - Carga: «esqueleto de la tabla con 5 filas».
   - Vacío: «mensaje “Aún no tienes pedidos” y botón “Ir a la tienda”».
   - Error: «aviso con “Reintentar”; un 401 redirige a `/login`».
   - Éxito: «tabla paginada de pedidos».
3. Si un estado no existe en el código (por ejemplo, el error deja la pantalla en blanco), no lo inventes: escribe «sin resolver» y pregunta a la persona si se resuelve en esta tarea.

## Resultado

- «Estados de UI» con los cuatro estados descritos, o con los que faltan marcados «sin resolver» y planteados a la persona.
