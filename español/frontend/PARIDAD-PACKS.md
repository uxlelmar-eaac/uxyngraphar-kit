# PARIDAD-PACKS — gobernanza de paridad entre los packs `frontend` (cliente) y `backend` (servidor)

Fuente única de verdad sobre **qué archivos comparten los dos packs** y **cuál es el lado canónico** al editarlos. Este archivo **viaja idéntico dentro de cada pack**; complementa la regla R-14 de `PROTOCOLO.md` y el `CHANGELOG.md` del pack.

> Nomenclatura: en la columna «Lado canónico», `cliente` = carpeta `frontend/` y `servidor` = carpeta `backend/`.

## Cómo usar esta matriz

1. **Antes de editar** un archivo que exista en ambos packs, buscar su fila aquí.
2. **`identico`** — debe ser byte-idéntico en ambos packs. Editar el canónico, copiar al otro, verificar con `python3 scripts/verificar-paridad.py`. Se admiten **patrones con `*`** (p. ej. README de estados).
3. **`adaptado`** — mismo contenido conceptual con terminología por pack (UI/BFF vs API/backend). Editar primero el **lado canónico** y replicar la adaptación en el otro **en el mismo cambio**; actualizar la fecha de la fila.
4. **`especifico`** — contenido propio de cada pack (stack, arquitectura); no requiere réplica.
5. Cambios de estructura (altas/bajas de archivos) → además de esta matriz, entrada en `CHANGELOG.md` y, en repos adoptados, ficha `EVO-*`.

La verificación automática solo opera cuando ambos packs están juntos (proyecto plantilla); en un repo aislado, `verificar-paridad.py` se desactiva solo. Además avisa de archivos sin fila en esta matriz y de filas «adaptado»/«especifico» cuyo archivo es idéntico en ambos packs. Detecta packs hermanos `cliente/servidor` o `frontend/backend`.

## Matriz

| Archivo (path relativo al pack) | Tipo | Lado canónico | Últ. sincronización |
|---------------------------------|------|---------------|---------------------|
| `.gitignore` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `00-nucleo/INDICE.md` | adaptado | servidor | 2026-09-14 |
| `00-nucleo/arquitectura.md` | especifico | cada pack | 2026-08-09 |
| `00-nucleo/ciclo-vinculante.md` | adaptado | servidor | 2026-08-09 |
| `00-nucleo/configuracion-proyecto.md` | adaptado | servidor | 2026-08-09 |
| `00-nucleo/convenciones-frontmatter.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/eficiencia-ia.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/ampliacion-alcance.md` | identico | ambos (sincronizar por hash) | 2026-10-26 |
| `00-nucleo/politica-idioma.md` | identico | ambos (sincronizar por hash) | 2026-10-28 |
| `00-nucleo/nombres-autoexplicativos.md` | identico | ambos (sincronizar por hash) | 2026-10-29 |
| `00-nucleo/glosario-dominio.md` | identico | ambos (plantilla P; sincronizar por hash) | 2026-10-28 |
| `00-nucleo/estrategia-instrucciones.md` | adaptado | servidor | 2026-08-09 |
| `00-nucleo/glosario.md` | especifico | cada pack | 2026-08-09 |
| `00-nucleo/mapa-dependencias.md` | adaptado | servidor | 2026-09-14 |
| `00-nucleo/plantilla-modulo.md` | especifico | cada pack | 2026-09-14 |
| `00-nucleo/registro-ids-compartidos.md` | adaptado | servidor | 2026-08-09 |
| `00-nucleo/limite-350-lineas.md` | adaptado | servidor | 2026-09-14 |
| `00-nucleo/restricciones.md` | especifico | cada pack | 2026-09-14 |
| `00-nucleo/vision-documentacion.md` | adaptado | servidor | 2026-08-09 |
| `05-instrucciones/INDICE.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `05-instrucciones/_PLANTILLA-adopcion-inicial-pack.md` | adaptado | servidor | 2026-08-09 |
| `05-instrucciones/_PLANTILLA-consolidar-espejo-integral.md` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `05-instrucciones/_PLANTILLA-generar-espejo-integral.md` | adaptado | servidor | 2026-08-09 |
| `05-instrucciones/_PLANTILLA-politica-espejo-incremental.md` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `05-instrucciones/_PLANTILLA-solo-documentacion.md` | adaptado | servidor | 2026-08-09 |
| `05-instrucciones/_PLANTILLA.md` | adaptado | servidor | 2026-08-09 |
| `05-instrucciones/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `10-guias/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/adopcion-pack.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/ci-validacion-documentacion.md` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `10-guias/organizacion-estados-fechas.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `10-guias/ciclo-integral-actos.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/contratos-api.md` | especifico | cada pack | 2026-08-09 |
| `10-guias/espejo-incremental-proyectos-grandes.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/flujo-instrucciones-documentacion.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/generar-documentacion-integral.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/herramientas-autorizadas-vs-propuestas.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/incorporacion.md` | especifico | cada pack | 2026-08-09 |
| `10-guias/instalacion-docs.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/mejoras-propuestas-ia.md` | adaptado | cliente | 2026-08-09 |
| `10-guias/monorepo-docs-fusionados.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/pruebas.md` | especifico | cada pack | 2026-08-09 |
| `10-guias/redaccion-lectura-minima.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/sistema-integral-vs-detalle.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/sync-documentacion-pr.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/sync-multi-repo.md` | adaptado | servidor | 2026-08-09 |
| `10-guias/tarjeta-referencia-humana.md` | adaptado | servidor | 2026-08-09 |
| `15-rutas/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `15-rutas/_PLANTILLA.md` | especifico | cada pack | 2026-08-09 |
| `15-rutas/_PROTOCOLO.md` | adaptado | servidor | 2026-08-09 |
| `20-decisiones/INDICE.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `20-decisiones/_PLANTILLA-ADR.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `20-decisiones/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `25-areas/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `25-areas/_PLANTILLA.md` | especifico | cada pack | 2026-08-09 |
| `25-areas/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `30-manuales/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `30-manuales/despliegue.md` | especifico | cada pack | 2026-08-09 |
| `30-manuales/incidentes.md` | especifico | cada pack | 2026-08-09 |
| `35-herramientas/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `35-herramientas/_PLANTILLA-autorizada.md` | adaptado | servidor | 2026-08-09 |
| `35-herramientas/_PLANTILLA-promover-desde-propuesta.md` | adaptado | servidor | 2026-08-09 |
| `35-herramientas/_PLANTILLA-propuesta.md` | adaptado | servidor | 2026-08-09 |
| `35-herramientas/_PROTOCOLO.md` | adaptado | cliente | 2026-08-09 |
| `35-herramientas/autorizadas/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `35-herramientas/autorizadas/README.md` | adaptado | servidor | 2026-08-09 |
| `35-herramientas/autorizadas/decisiones-pendientes.md` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `35-herramientas/propuestas/INDICE.md` | adaptado | servidor | 2026-08-23 |
| `35-herramientas/propuestas/README.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `40-auditorias/INDICE.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `40-auditorias/_PLANTILLA.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `40-auditorias/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `45-mejoras-propuestas/INDICE.md` | adaptado | servidor | 2026-08-23 |
| `45-mejoras-propuestas/_PLANTILLA-propuesta.md` | adaptado | servidor | 2026-08-23 |
| `45-mejoras-propuestas/_PLANTILLA-revisar-propuesta.md` | adaptado | servidor | 2026-08-23 |
| `45-mejoras-propuestas/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `46-evolucion-documentacion/INDICE.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `46-evolucion-documentacion/_PLANTILLA-cobertura.md` | adaptado | servidor | 2026-08-23 |
| `46-evolucion-documentacion/_PLANTILLA-proceso.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `46-evolucion-documentacion/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `46-evolucion-documentacion/matriz-cobertura-proyectos.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `46-evolucion-documentacion/*/*/EVO-*.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `50-sistema-integral/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `50-sistema-integral/_PLANTILLA-README-carpeta.md` | adaptado | servidor | 2026-08-09 |
| `50-sistema-integral/_PLANTILLA-archivo.md` | adaptado | servidor | 2026-09-14 |
| `50-sistema-integral/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `50-sistema-integral/mapa-capas.md` | adaptado | servidor | 2026-08-09 |
| `50-sistema-integral/registro-cobertura-espejo.md` | adaptado | servidor | 2026-08-09 |
| `50-sistema-integral/vision-espejo.md` | adaptado | servidor | 2026-08-09 |
| `00-nucleo/congelamiento.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/INDICE.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/adr.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/auditoria.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/bloques-decision.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/comunes.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/evolucion.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/ficha-ruta.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/herramienta.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/instruccion.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/mejora.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/frontmatter/reglas.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `10-guias/actualizar-nucleo.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `25-areas/_PLANTILLA-RESUMEN-area.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `40-auditorias/activas.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `55-automatizaciones/01-rutas-vivas.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/02-anclas-rotas.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/03-espejo-completo.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/04-decisiones-vinculantes.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/05-estados-con-fecha.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/06-herramientas-autorizadas.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/07-humo-integral.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/08-manuales-vivos.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/09-limite-lineas.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/10-registro-vinculos.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/INDICE.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `55-automatizaciones/_PLANTILLA.md` | adaptado | servidor | 2026-10-15 |
| `55-automatizaciones/_PROTOCOLO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/applier_rutas.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/session_acciones.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/test_decisiones_seguridad.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `90-archivo/INDICE.md` | adaptado | servidor | 2026-08-09 |
| `90-archivo/capacitacion/README.md` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `AGENTES.md` | adaptado | servidor | 2026-09-14 |
| `AGENTS.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `ESTADO.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `CHANGELOG.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `INDICE.md` | adaptado | servidor | 2026-08-09 |
| `PARIDAD-PACKS.md` | identico | ambos (este archivo) | 2026-08-09 |
| `PROTOCOLO.md` | adaptado | servidor | 2026-09-14 |
| `README.md` | adaptado | servidor | 2026-10-15 |
| `VERSION.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `REGLAS.md` | adaptado | servidor | 2026-09-14 |
| `scripts/decisiones/alcance.py` | identico | ambos (sincronizar por hash) | 2026-10-26 |
| `scripts/decisiones/test_alcance.py` | identico | ambos (sincronizar por hash) | 2026-10-26 |
| `scripts/decisiones/applier.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/applier_promocion.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/common.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/common_bloques.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/common_constantes.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/common_frontmatter.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/decisiones.py` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `scripts/decisiones/scanner.py` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `scripts/decisiones/session.py` | identico | ambos (sincronizar por hash) | 2026-08-09 |
| `scripts/decisiones/test_decisiones.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/test_decisiones_aplicacion.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/test_decisiones_fachada.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/actualizar-pack.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/archivado.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/metricas.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/plantillas.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/test_herramientas.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/ejecutar-pruebas.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/espejo/test_espejo.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/espejo/verificar_espejo.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/ganchos/instalar_ganchos.py` | identico | ambos (sincronizar por hash) | 2026-10-28 |
| `scripts/ganchos/test_ganchos.py` | identico | ambos (sincronizar por hash) | 2026-10-28 |
| `scripts/instalar-ganchos.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validacion/test_validar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validacion/validar_comun.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validacion/validar_enlaces.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validacion/validar_estructura.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validacion/validar_fichas.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validacion/validar_pack.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validacion/validar_vinculos.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/validar-documentacion.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/verificar-espejo.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/instalar-pack.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/escanear-secretos.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/control/secretos.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/control/escaneo.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/control/test_escaneo.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/nucleo/test_secretos.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/nucleo/test_servidor.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/nucleo/ci.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `46-evolucion-documentacion/03-completadas/2026-10-15/EVO-20261015-restriccion-credenciales.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/nucleo/test_multipack.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `46-evolucion-documentacion/03-completadas/2026-10-15/EVO-20261015-multipack-instalador.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/nucleo/flujo.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `46-evolucion-documentacion/03-completadas/2026-10-15/EVO-20261015-experiencia-instalacion.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/nucleo/test_doctor_gancho.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/nucleo/test_subcarpeta.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/controlar.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-28 |
| `scripts/control/uxyngraphar_config.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-28 |
| `scripts/control/puerta.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-28 |
| `scripts/control/test_control.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/control/idioma.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-28 |
| `scripts/control/test_idioma.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-28 |
| `10-guias/elegir-pack.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `10-guias/control-de-construccion.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `10-guias/configuracion-uxyngraphar.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `46-evolucion-documentacion/03-completadas/2026-10-15/EVO-20261015-control-construccion-universal.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-15 |
| `scripts/verificar-nucleo.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/depurar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/depurar_aplicar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/depurar_cli.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/test_depurar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/actualizar.py` | identico | ambos (sincronizar por hash) | 2026-10-29 |
| `scripts/nucleo/transaccion.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `scripts/nucleo/contrato.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `scripts/nucleo/migraciones.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `scripts/nucleo/test_transaccion.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `scripts/memoria.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `scripts/memoria/almacen.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `scripts/memoria/test_memoria.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `95-memoria/INDICE.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `10-guias/memoria.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-29 |
| `scripts/reglas.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/reglas/reglas_proyecto.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/reglas/test_reglas.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/control/reglas_control.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `96-reglas-proyecto/INDICE.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `96-reglas-proyecto/_PROTOCOLO.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `96-reglas-proyecto/_PLANTILLA-regla.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `96-reglas-proyecto/_PLANTILLA-excepcion.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `10-guias/ajustes-locales.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `10-guias/costo-tokens.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `10-guias/envio-sugerencias.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `10-guias/respaldos.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `97-ajustes-locales/INDICE.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `97-ajustes-locales/_PROTOCOLO.md` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/ajustes.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/ajustes/ajustes_locales.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/ajustes/test_ajustes.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/costo-tokens.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/evolucion/exportar.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/evolucion/test_exportar.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/exportar-evo.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/feedback.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/feedback/cliente.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/feedback/test_feedback.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/nucleo/respaldos.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/nucleo/test_respaldos.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/nucleo/test_zonas.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/nucleo/zonas.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/respaldos.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/tokens/costo.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/tokens/test_costo.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-30 |
| `scripts/nucleo/terminal.py` | identico | ambos (fuente: `_compartido/base`) | 2026-10-31 |
| `scripts/nucleo/clasificacion.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/instalar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/lock.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/proteccion.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/test_nucleo.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/verificar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/doctor.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/doctor.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/test_doctor.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/contexto.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/presupuesto.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/espejo-mapa.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/empaquetar-pack.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/flota.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/tokens/estimar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/tokens/paquete.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/tokens/medir.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/tokens/test_tokens.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/cerrar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/estado.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/decisiones/test_cerrar_estado.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/espejo/mapa.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/espejo/test_mapa.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/empaquetar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/analizar.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `scripts/nucleo/test_distribucion.py` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `05-instrucciones/_PLANTILLA-compacta.md` | identico | ambos (sincronizar por hash) | 2026-10-15 |
| `00-nucleo/agentes-detalle.md` | adaptado | servidor | 2026-10-15 |
| `scripts/verificar-paridad.py` | identico | ambos (sincronizar por hash) | 2026-10-28 |
| `*/01-pendientes/*/README.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `*/02-en-progreso/*/README.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `*/03-completadas/*/README.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `*/04-archivadas/*/README.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `*/05-canceladas/*/README.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `*/06-listas-para-eliminar/*/README.md` | identico | ambos (sincronizar por hash) | 2026-08-23 |
| `!00_franco-documentacion-practica.html` | especifico | cliente (solo existe ahí) | 2026-08-09 |
| `!00_banco-documentacion-practica.html` | especifico | servidor (solo existe ahí) | 2026-08-09 |
