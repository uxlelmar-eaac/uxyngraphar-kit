---
name: corregir-dependencia-de-capa
description: Resuelve un import que el perfil no permite moviendo código a la capa correcta o creando la frontera adecuada (contrato, puerto o integración).
resuelve: [capas-mal-importadas, modulos-acoplados, comun-dependiente-del-negocio]
---

# Corregir dependencia de capa

## Cuándo usarla

- `capas.py revisar` reporta una infracción en código que tocas.
- Vas a escribir un import que `COMPONENTES.md` no permite.

## Pasos

1. Lee el motivo de la infracción y elige el caso:
   - **Capa que no puede importar otra** (por ejemplo `domain` → `infrastructure`): invierte la dependencia. Define en la capa interna lo que necesita (una interfaz o puerto) y deja que la externa lo implemente.
   - **Tipo compartido en la capa equivocada**: muévelo a `contracts/` (servidor) o `types/` (cliente).
   - **Cruce de módulo fuera de `integrations/`**: crea o amplía `integrations/<otro>.integration.<ext>` con un método de propósito claro y llama a ese método.
   - **Común que importa negocio**: lo que tiene negocio vuelve a su módulo; lo común recibe lo que necesita por parámetro.
2. Haz el cambio mínimo: no reorganices el módulo entero.
3. Vuelve a revisar las rutas: `python3 $P/scripts/capas.py revisar <rutas>`.
4. Si ningún caso encaja sin romper un límite, no fuerces: pasa a la fase `registrar-desviacion`.

## Resultado

- La infracción desaparece sin crear otra, o queda propuesta una desviación para que la decida una persona.
