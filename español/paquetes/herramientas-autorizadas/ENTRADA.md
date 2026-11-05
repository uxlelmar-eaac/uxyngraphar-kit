# Herramientas autorizadas — entrada

Activado con «usa el paquete herramientas-autorizadas» / «sigue el protocolo herramientas» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/herramientas-autorizadas/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/herramientas-autorizadas/REGLAS.md`.
3. ¿Hay una herramienta autorizada que cubra el pedido? `python3 $S/fichas.py listar autorizada --status authorized`. Si encaja en su «Alcance permitido», ejecútala tal como dice (solo su ficha y sus anclas).
4. Si ves un procedimiento repetido que convendría autorizar, **propónlo**: `python3 $S/fichas.py nueva propuesta --slug <slug>`. No lo ejecutes como herramienta.
5. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-herramientas.py`.

Persona: autorizar = `python3 $S/fichas.py nueva autorizada --slug <slug> --humano` (o promover una propuesta copiándola) y `fichas.py estado <propuesta> promovida --humano`.
