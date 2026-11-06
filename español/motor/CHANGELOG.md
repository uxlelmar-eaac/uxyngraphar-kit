# Cambios

## 2.0.0

- uxyngraphar pasa de dos packs documentales (servidor/cliente) a un catálogo de paquetes de gobernanza temáticos, portátiles e inmutables: `instrucciones-aprobadas`, `calidad-de-codigo`, `secretos-y-credenciales`, `decisiones-de-arquitectura`, `rutas-de-api`, `paginas-de-interfaz`, `mapa-de-modulos`, `documentacion-espejo`, `herramientas-autorizadas`, `auditorias-tecnicas`, `deuda-y-mejoras`, `manuales-operativos`, `memoria-e-historial`, `reglas-del-proyecto`, `evolucion-del-sistema`, `revision-humana`, `contratos-entre-repositorios`, `arquitectura-monolitica-por-capas`, `verificaciones-vivas`, `paginas-de-aterrizaje-bento` y `experiencia-de-usuario`.
- Lo que decide una persona lo ejecuta una persona: los status `solo_humano` exigen `--humano` y una terminal interactiva (o `UXYNGRAPHAR_HUMANO=1`); `revision-humana` reúne lo que espera decisión y lo aplica en tanda.
- Paquete base: `instalar … --base <id>` deja `FLUJO.json` en `trabajar_con` y el agente lo aplica en cada pedido sin que se nombre.
- La instalación genera las protecciones (`.claude/settings.json`, `.cursorignore`) a partir de los paquetes instalados.
- En cada repo, una sola carpeta `uxyngraphar/` con `paquetes/` (instalados, inmutables), `trabajo/`, `INDICE.md` y `FLUJO.json` para decidir cómo trabaja el agente. Nada se activa solo: sin ganchos git ni puerta de commits.
- Fichas en `uxyngraphar/trabajo/<paquete>/[<tipo>/]<estado>/<id>.md`, sin números ni carpetas por fecha.
- Cada paquete: `README.md` (pasos + reglas), `paquete.json`, `docs/`, `plantillas/` y `scripts/` (con su propio `scripts/comun/`); completo ya en el catálogo, sin código inyectado al construir.
- El kit queda en `español/motor/` (herramienta, instalador, pruebas y documentación) y `español/paquetes/`, con `paquetes/!base/` como base común de la que nacen los paquetes nuevos.
- `uxyngraphar migrar` lleva instalaciones 1.x a 2.0 con simulación, respaldo, verificación sha256 y reversión.
- Nomenclatura propia del kit (`motor/NOMENCLATURA.md`): id `<objeto>-<enlace>-<calificador>`, título = id con tildes, campo `familia`, prefijos de 3 letras únicos, vocabulario de status, frases de activación que no se pisan y scripts por tema. `validar` y `crear` la comprueban; `uxyngraphar nomenclatura` lista los status heredados del 1.x. Renombrados: `contratos-entre-repos` → `contratos-entre-repositorios`, `landing-bento` → `paginas-de-aterrizaje-bento`; en `paginas-de-interfaz` el tipo `ruta` (RUT) pasa a `pagina` (PAG); en `reglas-del-proyecto` RP/EX/AJ pasan a REG/EXC/AJL; scripts `calidad.py`, `secretos.py`, `secretos_patrones.py`, `revision.py`, `verificar-paginas.py`.
- Se retiran los packs 1.x, su instalador por proyecto y su documentación.
