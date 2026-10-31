# Mapa de dependencias del canon (cliente)

Qué gobierna cada documento del núcleo y quién depende de él. Al **editar un documento del canon**, revisar su columna derecha en el mismo cambio o registrar ficha `EVO-*`. Precedencia ante conflictos: [PROTOCOLO.md](../PROTOCOLO.md) → Jerarquía normativa.

| Documento canon | Gobierna | Dependen de él (principales) |
|-----------------|----------|------------------------------|
| [../PROTOCOLO.md](../PROTOCOLO.md) | Taxonomía, reglas duras R-01–R-25, jerarquía normativa | Todo el pack; `AGENTES.md` y `REGLAS.md` (resúmenes) |
| [eficiencia-ia.md](eficiencia-ia.md) | Presupuesto 8/5 (R-06), matriz de lectura, fases | AGENTES, REGLAS, plantillas 05, [redaccion-lectura-minima](../10-guias/redaccion-lectura-minima.md) |
| [ciclo-vinculante.md](ciclo-vinculante.md) | Actos, vínculos, colas al cierre, presupuesto por acto | Plantillas 05, convenciones (`acto`), [ciclo-integral-actos](../10-guias/ciclo-integral-actos.md), [flujo-instrucciones](../10-guias/flujo-instrucciones-documentacion.md) |
| [estrategia-instrucciones.md](estrategia-instrucciones.md) | Capas documentales, reglas del espejo | [50/_PROTOCOLO](../50-sistema-integral/_PROTOCOLO.md), guías de espejo, plantillas de espejo |
| [convenciones-frontmatter.md](convenciones-frontmatter.md) | Campos y enums de todas las fichas; bloques de decisión | Todas las plantillas, `scripts/decisiones/`, `validar-documentacion.py` |
| [../10-guias/organizacion-estados-fechas.md](../10-guias/organizacion-estados-fechas.md) | Estructura estados + fechas, mapeo `status` ↔ carpeta, alcance de 46 (R-17, R-18) | PROTOCOLO, protocolos de sección, `scripts/decisiones/`, `validar-documentacion.py` |
| [configuracion-proyecto.md](configuracion-proyecto.md) | Identidad, raíces del espejo, versión y perfil adoptados | Plantillas de espejo, adopción, registro de ids |
| [registro-ids-compartidos.md](registro-ids-compartidos.md) | Contratos API por id (esquema único) | CONTEXTO de áreas, [sync-multi-repo](../10-guias/sync-multi-repo.md), monorepo, espejo |
| [arquitectura.md](arquitectura.md) · [plantilla-modulo.md](plantilla-modulo.md) · [restricciones.md](restricciones.md) · [limite-350-lineas.md](limite-350-lineas.md) | Canon técnico UI del repo destino + límite 350 líneas (R-19) | CONTEXTO de áreas, ADRs |
| [glosario.md](glosario.md) | Vocabulario | Lectura humana |
