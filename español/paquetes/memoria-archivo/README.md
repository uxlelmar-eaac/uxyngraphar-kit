# Memoria y archivo

Activado con «usa el paquete memoria-archivo» / «sigue el protocolo memoria» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/memoria-archivo/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Solo si el pedido lo pide expresamente: busca en la memoria con `python3 $S/memoria.py buscar <texto>` y abre únicamente las notas que devuelva.
4. Para guardar conocimiento que la persona quiere conservar: `python3 $S/comun/fichas.py nueva nota --slug <slug> --titulo "…"`.
5. Archivar un documento (persona): `python3 $S/memoria.py archivar <ruta> --humano`.
6. Antes de terminar: `python3 $S/comun/verificar.py`.

Trabajo: `uxyngraphar/trabajo/memoria-archivo/memoria/` (notas) y `…/archivo/<AAAA-MM-DD>/` (histórico).

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Lectura solo bajo pedido.** El agente no lee, busca ni resume `memoria/` ni `archivo/` salvo que el pedido lo pida expresamente; y entonces solo lo que devuelva `memoria.py buscar`.
2. **El archivo es histórico e inmutable:** nada en `archivo/` se edita ni se borra; solo se añade.
3. **Archivar es una acción de la persona** (`memoria.py archivar … --humano`).
4. **Notas breves y fechadas**, con la fuente (conversación, incidente, decisión) y cuándo deja de ser válida.
5. **Sin secretos ni datos personales** en notas o archivo.
