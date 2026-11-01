# Sugerencias EVO

Las fichas en `46-evolucion-documentacion/` describen mejoras del **sistema documental**.

## Opt-in

- Pregunta al instalar/actualizar; **sin opción premarcada**
- Con `--si` y **sin** `--colaborar` → cuenta como **No**
- Con **Sí**: se pueden enviar EVO nuevas/cambiadas tras `instalar`/`actualizar` **humanos**
- Nunca desde CI, ganchos ni el agente
- No se envía código, rutas crudas, correos ni métricas de uso
- Antes de preguntar se muestra qué sale y qué no; se cambia cuando quieras con `feedback.py activar` o `revocar`
- Receptor oficial: el backend de uxyngraphar (repo `uxyngraphar-backend`)

## Comandos en el proyecto

```bash
python3 uxyngraphar/scripts/feedback.py previsualizar
python3 uxyngraphar/scripts/feedback.py estado
python3 uxyngraphar/scripts/feedback.py activar --acepto          # tras leer qué se envía
python3 uxyngraphar/scripts/feedback.py activar --acepto --url URL  # receptor alternativo
python3 uxyngraphar/scripts/feedback.py enviar                    # pendientes
python3 uxyngraphar/scripts/feedback.py enviar --todas
python3 uxyngraphar/scripts/feedback.py revocar
python3 uxyngraphar/scripts/feedback.py revocar --borrar-remoto
```

La IA **no** debe ejecutar `activar` / `enviar` por su cuenta.

Guía canónica: `uxyngraphar/10-guias/envio-sugerencias.md`.
