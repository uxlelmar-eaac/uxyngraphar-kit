# Memoria y archivo — entrada

Activado con «usa el paquete memoria-archivo» / «sigue el protocolo memoria» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/memoria-archivo/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/memoria-archivo/REGLAS.md`.
3. Solo si el pedido lo pide expresamente: busca en la memoria con `python3 $S/memoria.py buscar <texto>` y abre únicamente las notas que devuelva.
4. Para guardar conocimiento que la persona quiere conservar: `python3 $S/fichas.py nueva nota --slug <slug> --titulo "…"`.
5. Archivar un documento (persona): `python3 $S/memoria.py archivar <ruta> --humano`.
6. Antes de terminar: `python3 $S/verificar.py`.

Trabajo: `uxyngraphar-work/memoria-archivo/memoria/` (notas) y `…/archivo/<AAAA-MM-DD>/` (histórico).
