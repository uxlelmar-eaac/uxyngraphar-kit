# Calidad de código — entrada

Activado con «usa el paquete calidad-codigo» / «sigue el protocolo calidad» o por `uxyngraphar-work/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/calidad-codigo/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/calidad-codigo/REGLAS.md`; guías en `guias/` (`limite-lineas.md`, `nombres.md`, `idioma.md`).
3. Mientras trabajas, aplica las reglas a todo lo que escribas.
4. Antes de terminar: `python3 $S/revisar.py` (todo) o `python3 $S/revisar.py <archivos>` (solo los tuyos); `--commits` revisa también los últimos mensajes de commit.
   - Un archivo que tú hiciste crecer por encima del límite se divide en esta misma tarea (guía `limite-lineas.md`).
   - Un archivo que ya excedía y no tocaste: avísalo, no lo dividas por tu cuenta.

Ajustes (persona): `uxyngraphar-work/calidad-codigo/ajustes.json` (`raices`, `extensiones`, `excluir`, `limite_lineas`, `exenciones_lineas`).
