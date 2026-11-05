# Memoria y archivo — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Lectura solo bajo pedido.** El agente no lee, busca ni resume `memoria/` ni `archivo/` salvo que el pedido lo pida expresamente; y entonces solo lo que devuelva `memoria.py buscar`.
2. **El archivo es histórico e inmutable:** nada en `archivo/` se edita ni se borra; solo se añade.
3. **Archivar es una acción de la persona** (`memoria.py archivar … --humano`).
4. **Notas breves y fechadas**, con la fuente (conversación, incidente, decisión) y cuándo deja de ser válida.
5. **Sin secretos ni datos personales** en notas o archivo.
