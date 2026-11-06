# Evolución del sistema de gobernanza

Activado con «usa el paquete evolucion-del-sistema» / «sigue el protocolo evolucion» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/evolucion-del-sistema/scripts`.

Los paquetes son inmutables: este es el canal para mejorarlos. Una EVO describe lo que le falta **al sistema** (un paquete, una plantilla, un proceso), nunca al producto.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Si al trabajar notas que un paquete no cubre el caso: `python3 $S/comun/fichas.py nueva evo --slug <slug> --titulo "…"` con evidencia y propuesta. **No cambies el paquete.**
4. Si la persona lo pide, consulta o crea la matriz de cobertura: `python3 $S/evolucion.py matriz`.
5. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-evolucion.py`.

Persona: aprobar `fichas.py estado EVO-… approved --humano`; llevarla al catálogo con `python3 $S/evolucion.py exportar --humano` (informe en `trabajo/evolucion-del-sistema/exportaciones/`); si urge en este proyecto, un ajuste local en `reglas-del-proyecto` que cite la EVO; al publicarse la versión que la incorpora, `done`.

Trabajo: `uxyngraphar/trabajo/evolucion-del-sistema/<estado>/` y `MATRIZ-COBERTURA.md`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: una EVO aprobada que llega al catálogo.

1. **Del sistema, no del producto.** Deuda o bugs del producto van a `deuda-y-mejoras`; investigaciones, a `auditorias-tecnicas`; documentación de un módulo, a su paquete.
2. **Registrar, no aplicar.** Nunca edites un paquete instalado ni su copia del catálogo para resolver una EVO.
3. **Máximo `max_por_tarea` (2) EVO nuevas por tarea**, con evidencia y propuesta concretas.
4. **Lectura mínima:** no abras las EVO en tareas normales; solo al registrar una (para evitar duplicados: `fichas.py listar evo --status pending`) o si la persona lo pide.
5. **Solo una persona** aprueba, rechaza o da por hecha una EVO, y decide si se exporta. Nada se envía solo.
6. **Estado real:** una EVO `pending` afirma que el cambio no está aplicado en el sistema. Nunca `pending` si ya se aplicó.
