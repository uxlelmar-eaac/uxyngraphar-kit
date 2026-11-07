---
name: crear-modulo
description: Crea un módulo de negocio nuevo con las capas del perfil usando el andamiaje del paquete, y lo deja sin infracciones.
resuelve: [modulos-sin-estructura-uniforme]
---

# Crear módulo

## Cuándo usarla

- El pedido introduce un área funcional que no tiene módulo.
- La fase `disenar-modulo` la cita.

## Pasos

1. Elige la variante según el perfil: `modulo-servidor` o `modulo-cliente`.
2. Simula: `python3 $P/scripts/comun/andamiar.py <variante> --nombre <nombre>`. Revisa que el destino sea el esperado y que no exista nada.
3. Crea: `python3 $P/scripts/comun/andamiar.py <variante> --nombre <nombre> --aplicar`. Nunca sobrescribe; lo que ya existía aparece como «omitido».
4. Borra las capas que el módulo no necesita: no se dejan capas vacías ni de relleno.
5. Si el framework exige un archivo raíz (por ejemplo `<nombre>.module.ts`), créalo en la raíz del módulo.
6. Usa nombres relacionales: `<raiz>.<relacion>.<ext>` (`orders.controller.ts`, `orders.usecase.ts`, `orders.api.ts`). Nunca `*-parte2`, `*-nuevo` ni `utils2`.
7. Si están instalados, registra el módulo en sus paquetes: su área en `mapa-de-modulos`, sus rutas en `rutas-de-api` o `paginas-de-interfaz` y sus fichas en `documentacion-espejo`.
8. Comprueba: `python3 $P/scripts/capas.py revisar src/modules/<nombre>` sin infracciones.

## Resultado

- `src/modules/<nombre>/` con las capas necesarias, imports dentro del perfil y `capas.py revisar` limpio.
