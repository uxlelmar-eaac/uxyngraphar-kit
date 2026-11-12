# 0012 · La biblioteca de la cuenta se sincroniza con la caché local

- **Estado:** aceptada
- **Fecha:** 2026-11-11
- **Plan:** `PLAN-PLATAFORMA/` (raíz de uxyngraphar), fase 4

## Contexto

Con el Mercado, una persona obtiene sistemas gratuitos, compra sistemas de pago y crea sistemas privados. Los de pago
y los privados no aparecen en el índice público (`/v1/sistemas/indice`), así que `traer` no los encuentra.

## Decisión

1. `GET /v1/me/biblioteca` (con la sesión del kit, ADR 0011) devuelve los sistemas de la biblioteca con su última
   versión, `sha256`, motor requerido y origen (`FREE`, `PURCHASE`, `OWNER`, `GRANT`).
2. `uxyngraphar sincronizar` descarga a la caché (`~/.uxyngraphar/sistemas-de-gobernanza/<editor>/<id>/<version>/`) lo
   que falte, con la misma verificación que `traer` (huella del índice de la biblioteca + `INTEGRIDAD.json`). Se ejecuta
   también al iniciar sesión y al abrir el panel.
3. Lo descargado se guarda en `biblioteca.json` de la caché, que `fuentes.py` une con el índice público: así `instalar`
   y los avisos de actualización funcionan también con sistemas privados y comprados, y sin red.
4. **Nada se actualiza solo en los proyectos** (ADR 0002, 0003): el panel muestra «Actualización disponible» por repo y
   la persona decide.

## Consecuencias

- Un sistema comprado sigue funcionando sin red en los repos donde ya está instalado, aunque luego se reembolse.
- Los archivos de un sistema comprado son legibles en el equipo; la licencia (uso y modificación propios, sin
  redistribuir) es la protección, no el cifrado.
