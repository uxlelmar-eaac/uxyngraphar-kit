# Checklist de puesta en marcha

Marca en orden. La IA debe devolver este checklist al humano al terminar.

## Máquina

- [ ] Python ≥ 3.10 (`python3` o `py -3`)
- [ ] git disponible
- [ ] `uxyngraphar version` OK **o** clon con `español/instalar.py`
- [ ] Si falló el comando: PATH / terminal nueva ([herramienta.md](herramienta.md))

## Proyecto

- [ ] Pack sembrado (`docs/.uxyngraphar.lock` existe en la ruta correcta)
- [ ] Layout monorepo/multi-repo confirmado (subs / `--proyecto2`) si aplica
- [ ] `AGENTES.md` junto al `docs/` sembrado
- [ ] Commit inicial de `docs/` + `AGENTES.md` (sin secretos)

## Configuración

- [ ] `docs/00-nucleo/configuracion-proyecto.md` rellenado
- [ ] Arquitectura / restricciones / registro-ids revisados
- [ ] `docs/uxyngraphar.config.json` coherente (persona vía panel)
- [ ] Colaborar EVO decidido — con `--si` sin flag = No (en CI o con un agente queda pendiente); la IA no activa feedback

## Verificación

- [ ] `python3 docs/scripts/doctor.py` (o ruta en subcarpeta) sin errores bloqueantes
- [ ] (Opcional) `validar-documentacion.py` y `decisiones/decisiones.py scan`
- [ ] CI con `controlar.py` si el repo es compartido

## Handoff humano

- [ ] Persona sabe aprobar instrucciones ([../03-uso-humano/aprobar-instrucciones.md](../03-uso-humano/aprobar-instrucciones.md))
- [ ] Persona conoce el panel ([../03-uso-humano/panel.md](../03-uso-humano/panel.md))
- [ ] Si algo falla: [fallos-comunes.md](fallos-comunes.md)
