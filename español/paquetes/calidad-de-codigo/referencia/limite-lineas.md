# Límite de líneas y división relacional

**Por qué:** archivos cortos caben en el contexto de una persona y de un agente, se revisan mejor y concentran una sola responsabilidad.

## Cómo dividir

1. Identifica responsabilidades del archivo (validación, cálculo, acceso a datos, presentación, tipos).
2. Extrae cada una a un archivo hermano con el nombre original + sufijo de responsabilidad:
   - `checkout-page.tsx` → `checkout-page.summary.tsx`, `checkout-page.payment-form.tsx`
   - `user_service.py` → `user_service_queries.py`, `user_service_validation.py`
3. El archivo original queda como fachada: compone y reexporta; no duplica lógica.
4. Mueve las pruebas junto a la parte que prueban.
5. Ejecuta `calidad.py` y las pruebas del proyecto.

## Qué no hacer

- Dividir por número de líneas («parte1», «parte2»).
- Comprimir código (líneas larguísimas) para esquivar el límite.
- Pedir una exención: la decide una persona, nunca el agente.
