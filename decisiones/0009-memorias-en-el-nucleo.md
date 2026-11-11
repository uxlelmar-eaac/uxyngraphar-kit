# 0009 · Memorias del proyecto en el núcleo obligatorio de cada sistema

- **Estado:** aceptada
- **Fecha:** 2026-11-11

## Contexto

Al trabajar con un sistema, el agente y la persona acuerdan cosas del proyecto (excepciones aceptadas, nombres, rutas,
preferencias) que no son fichas ni reglas y se pierden entre conversaciones. Un sistema opcional de notas que el agente
solo lee si el pedido lo pide no basta: las notas no llegan al trabajo de los demás sistemas y solo existen si alguien
instala ese sistema.

## Decisión

1. **Núcleo:** todo sistema lleva `MEMORIAS.md` (`# Memorias`, «Qué recordar», «Qué no recordar») con la guía de su tema, y
   `scripts/comun/` trae `uxyn_memorias.py` y `memorias.py`.
2. **Dónde:** las memorias del proyecto viven en `uxyngraphar/trabajo/<id>/memorias/MEM-AAAAMMDD-slug.md`, fuera del sistema
   (que sigue siendo inmutable, ADR 0002). La carpeta `memorias` y el prefijo `MEM` quedan reservados.
3. **Quién:** el agente solo crea memorias `propuesta`; `vigente` y `archivada` los pone una persona (`--humano` o el panel).
   Las memorias del agente aprobadas llevan `aprobada_por: persona`, y `verificar.py` lo exige.
4. **Cuándo:** el agente las lee siempre al activar el sistema (paso fijo del bloque de entrada, justo después de
   `SISTEMA.md`) y aplica las vigentes no caducadas. Activar el sistema sigue siendo lo único que las pone en juego (ADR 0003).

## Consecuencias

- El servidor exige `MEMORIAS.md` en todo artefacto.
- La pestaña «Memorias» del panel reúne las propuestas pendientes de cada proyecto; la portada avisa de ellas.
