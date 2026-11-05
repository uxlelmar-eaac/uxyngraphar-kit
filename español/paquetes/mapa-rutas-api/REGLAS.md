# Mapa de rutas de API — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Una ficha por endpoint** (método + ruta). No hay dos fichas activas con la misma combinación.
2. **Ficha viva:** todo cambio de contrato (ruta, método, autenticación, roles, entrada, salida, errores) actualiza la ficha en la misma tarea.
3. **Contrato antes que implementación:** «Entrada» y «Salida» describen lo que ve el cliente, incluidos códigos de error relevantes.
4. **Archivos ancla reales:** rutas existentes en el repo (controlador, caso de uso, DTO, pruebas).
5. **Seguridad explícita:** `auth` (`public`, `bearer`, `cookie`, `api-key`…) y `roles` siempre declarados; un endpoint público se justifica en «Hace».
6. **Agrupar por módulo:** `--en <modulo>`.
7. **No borrar fichas:** un endpoint eliminado pasa a `retirada`; uno en desuso, a `deprecada` con la alternativa.
