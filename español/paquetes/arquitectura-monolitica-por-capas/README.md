# Arquitectura monolítica por capas

<!-- uxyngraphar:entrada:inicio -->
Activado con «usa el paquete arquitectura-monolitica-por-capas» / «sigue el protocolo arquitectura monolitica por capas» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `P=uxyngraphar/paquetes/arquitectura-monolitica-por-capas`.

1. Integridad: `python3 $P/scripts/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Alcance: lee `$P/PAQUETE.md`. Si el pedido cae en «Fuera de alcance», dilo y propón el paquete indicado; no lo resuelvas aquí.
3. Límites: lee `$P/LIMITES.md`; se cumplen en todo el trabajo.
4. Proceso, en orden: `$P/proceso/diagnosticar.md` → `$P/proceso/disenar-modulo.md` → `$P/proceso/implementar.md` → `$P/proceso/verificar.md` → `$P/proceso/registrar-desviacion.md`. Cada fase dice qué skills usar y cuándo está terminada.
5. Skills: en `$P/skills/<nombre>/SKILL.md`; léelas cuando una fase las cite o el pedido encaje con su descripción.
6. Consulta cuando haga falta: `$P/COMPONENTES.md` (piezas que define), `$P/HERRAMIENTAS.md` (scripts), `$P/referencia/` (guías), `$P/ejemplos/` (casos resueltos).
7. Andamiaje: `python3 $P/scripts/comun/andamiar.py <variante> --nombre <nombre>` muestra lo que crearía; con `--aplicar` lo crea sin sobrescribir. Variantes: `modulo-servidor`, `modulo-cliente`.
8. Trabajo: escribe solo en `uxyngraphar/trabajo/arquitectura-monolitica-por-capas/` y, en el código del proyecto, solo lo que el pedido pida.
9. Antes de terminar: `python3 $P/scripts/comun/verificar.py`, `python3 $P/scripts/verificar-capas.py`.

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo; los cambios se hacen en el catálogo.
<!-- uxyngraphar:entrada:fin -->

## En una frase

Cada módulo (`modulos` en ajustes, p. ej. `src/modules/*`) se divide en capas según el `perfil` (`servidor` o `cliente`); el perfil dice qué capa puede importar a cuál, los cruces entre módulos solo salen de `integrations/` y el código común no importa módulos.

## Lo que decide la persona

- Ajustes en `uxyngraphar/trabajo/arquitectura-monolitica-por-capas/ajustes.json`: `perfil`, `nivel` (`aviso` o `bloqueante`), `raices`, `modulos`, `comun` y `alias`.
- El documento del proyecto: `python3 $P/scripts/capas.py iniciar` crea `ARQUITECTURA.md` en el trabajo del paquete; lo edita una persona o una instrucción aprobada.
- Las desviaciones: solo con una ADR aceptada.
