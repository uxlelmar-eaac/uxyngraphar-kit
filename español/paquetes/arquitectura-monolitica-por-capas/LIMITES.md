# Límites

Se cumplen en todo el trabajo del paquete. Romper uno lo decide una persona con una ADR aceptada.

1. **Respeta las capas del perfil.** Una capa solo importa las que su perfil permite (ver `COMPONENTES.md`). Si una dependencia no está permitida, muévela a la capa correcta o crea la frontera (un contrato, un puerto, `integrations/`).
2. **Los cruces entre módulos solo salen de `integrations/`**, con pocos métodos y de nombre estable (`ensureOrderExists`, `notifyPayment`). El archivo raíz del módulo (registro en el framework) es la única otra excepción.
3. **Lo común no depende del negocio.** Nada bajo `comun` importa un módulo de `modulos`.
4. **El dominio es puro:** sin framework, ORM ni IO en `domain/`.
5. **No introduzcas infracciones nuevas**, aunque el `nivel` sea `aviso`. Las heredadas se registran como deuda y se corrigen por tandas.
6. **Romper una restricción exige una ADR aceptada** y su anotación en «Desviaciones aceptadas» de `ARQUITECTURA.md`.
7. **No cambies los ajustes** (`perfil`, `nivel`, `modulos`, `comun`, `alias`): son de la persona.

## Cuándo detenerse y preguntar

- La única solución que ves rompe una restricción: propón la ADR y espera.
- El código no encaja en ningún módulo ni en lo común (¿módulo nuevo o común?).
- `capas.py revisar` reporta infracciones que no introdujiste y el pedido no las incluye.
- El proyecto no sigue el perfil configurado (¿cambiar el perfil o adaptar el código?).
