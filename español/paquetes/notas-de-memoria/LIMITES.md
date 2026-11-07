# Límites

Se cumplen en todo el trabajo del paquete.

1. **Memoria solo bajo pedido.** El agente no lee, busca ni resume `memoria/` salvo que el pedido lo pida expresamente; y entonces solo lo que devuelva `notas.py buscar`.
2. **Notas breves y fechadas**, con la fuente (conversación, incidente, decisión) y cuándo deja de ser válida.
3. **Una nota que deja de valer se archiva, no se borra:** pasa a `archivada` con la causa escrita y sigue en `memoria/`.
4. **Sin secretos ni datos personales** en las notas.

## Cuándo detenerse y preguntar

- El pedido podría resolverse mejor con algo de la memoria, pero no la menciona: pregunta si quiere que busques en ella.
- La persona pide guardar algo que es una decisión técnica, una regla del código o un procedimiento: propón el paquete adecuado antes de crear la nota.
- Una nota contradice el código o el pedido actual: pregunta si sigue vigente antes de usarla.
- La persona quiere retirar un documento entero sin perderlo: propón `documentos-archivados`.
