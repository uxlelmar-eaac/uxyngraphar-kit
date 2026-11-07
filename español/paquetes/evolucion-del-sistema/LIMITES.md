# Límites

Se cumplen en todo el trabajo del paquete. Los cambios a un paquete llegan solo por una EVO aprobada que se incorpora al catálogo.

1. **Del sistema, no del producto.** Deuda o bugs del producto van a `deuda-y-mejoras`; investigaciones, a `auditorias-tecnicas`; documentación de un módulo, a su paquete.
2. **Registrar, no aplicar.** Nunca edites un paquete instalado ni su copia del catálogo para resolver una EVO.
3. **Máximo `max_por_tarea` (2) EVO nuevas por tarea**, con evidencia y propuesta concretas.
4. **Lectura mínima:** no abras las EVO en tareas normales; solo al registrar una (para evitar duplicados: `fichas.py listar evo --status pending`) o si la persona lo pide.
5. **Solo una persona** aprueba, rechaza o da por hecha una EVO, y decide si se exporta. Nada se envía solo.
6. **Estado real:** una EVO `pending` afirma que el cambio no está aplicado en el sistema. Nunca `pending` si ya se aplicó.
7. **La matriz es de la persona.** `MATRIZ-COBERTURA.md` se crea con `evolucion.py matriz`; el agente propone cambios, no los escribe por su cuenta.

## Cuándo detenerse y preguntar

- No está claro si la carencia es del sistema o del producto.
- La tarea no puede seguir sin el cambio en el paquete: propón a la persona un ajuste local en `adaptaciones-de-paquetes` y espera.
- Ya registraste `max_por_tarea` EVO en esta tarea.
- La persona pide exportar: el comando es suyo (`--humano`).
