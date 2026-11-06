# Arquitectura por capas

Activado con «usa el paquete arquitectura-por-capas» / «sigue el protocolo arquitectura» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/arquitectura-por-capas/scripts`.

Cada módulo (`modulos` en ajustes, p. ej. `src/modules/*`) se divide en capas según el `perfil` (`servidor` o `cliente`). El perfil dice qué capa puede importar a cuál; los cruces entre módulos solo salen de `integrations/`; el código común no importa módulos.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo) y `uxyngraphar/paquetes/arquitectura-por-capas/docs/restricciones.md`.
3. Si existe, lee `uxyngraphar/trabajo/arquitectura-por-capas/ARQUITECTURA.md` (lo concreto de este repo). Para orientarte: `python3 $S/capas.py mapa`.
4. Módulo nuevo: sigue `uxyngraphar/paquetes/arquitectura-por-capas/plantillas/modulo.md`.
5. Antes de terminar, sobre lo que tocaste: `python3 $S/capas.py revisar <rutas>`; y `python3 $S/comun/verificar.py` y `python3 $S/verificar-capas.py`.

Persona: `perfil`, `nivel` (`aviso` o `bloqueante`), `modulos`, `comun` y `alias` en `uxyngraphar/trabajo/arquitectura-por-capas/ajustes.json`; el documento del proyecto con `python3 $S/capas.py iniciar`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Respeta las capas del perfil.** Si una dependencia no está permitida, muévela a la capa correcta o crea la frontera (`integrations/`, un contrato, un puerto).
2. **Cruces de módulo solo por `integrations/`**, con métodos pocos y de nombre estable.
3. **Lo común no depende del negocio.**
4. **No introduzcas infracciones nuevas**, aunque el `nivel` sea `aviso`: las existentes se corrigen por tandas, como deuda registrada.
5. **Romper una restricción exige una ADR aceptada** y su anotación en «Desviaciones aceptadas» de `ARQUITECTURA.md`.
