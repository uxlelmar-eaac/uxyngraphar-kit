# Sugerencias EVO

Las fichas en `46-evolucion-documentacion/` describen mejoras del **sistema documental**.

## Opt-in

- Pregunta al instalar/actualizar; **sin opción premarcada**
- Con `--si` y **sin** `--colaborar` → cuenta como **No**
- Con **Sí**: se pueden enviar EVO nuevas/cambiadas tras `instalar`/`actualizar` **humanos**
- Nunca desde CI, ganchos ni el agente
- No se envía código, rutas crudas, correos ni métricas de uso

## Comandos en el proyecto

```bash
python3 docs/scripts/feedback.py previsualizar
python3 docs/scripts/feedback.py estado
python3 docs/scripts/feedback.py activar --acepto          # tras leer qué se envía
python3 docs/scripts/feedback.py activar --acepto --url URL  # receptor alternativo
python3 docs/scripts/feedback.py enviar                    # pendientes
python3 docs/scripts/feedback.py enviar --todas
python3 docs/scripts/feedback.py revocar
python3 docs/scripts/feedback.py revocar --borrar-remoto
```

La IA **no** debe ejecutar `activar` / `enviar` por su cuenta.

Guía canónica: `docs/10-guias/envio-sugerencias.md`.
