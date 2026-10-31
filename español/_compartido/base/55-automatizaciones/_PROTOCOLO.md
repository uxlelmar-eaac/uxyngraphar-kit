# Protocolo de automatizaciones

## Nomenclatura de especificación

```
55-automatizaciones/<NN>-<nombre>.md
```

`NN` estable (01–09). La implementación en el proyecto usa el mismo nombre:

```
<proyecto>/automatizaciones/<nombre>[.sh|.py|…]
```

## Obligatorio en cada especificación

1. **Fuente** — sección exacta de la documentación que manda.
2. **Valida** — qué comprueba, en 1–3 frases.
3. **Procedimiento** — pasos que la implementación debe seguir.
4. **Aceptación** — criterios verificables de pasa/no-pasa.
5. **Salida** — formato del reporte (lista de hallazgos con archivo y línea).

## Reporte estandarizado (obligatorio)

Toda corrida de una automatización desemboca en una **auditoría** en
`40-auditorias/` siguiendo su protocolo (R-17):

- Archivo `AUD-YYYYMMDD-<nombre-auto>.md` en `02-en-progreso/YYYY-MM-DD/`.
- Frontmatter de auditoría (`id`, `status: activa`, `severidad`, `areas`,
  `findings_count`, `related_instrucciones`).
- Cuerpo: preguntas, método, **hallazgos con evidencia (path:línea)**,
  recomendaciones, promociones propuestas.
- La sección `Salida` de cada especificación define las filas de hallazgos;
  el formato del reporte es siempre el de auditoría, nunca ad-hoc.
- Hallazgos siempre en **tabla** (`hallazgo | evidencia path:línea |
  severidad`); prohibida la prosa larga en resultados. La prosa va solo en
  recomendaciones, máximo 5 líneas.
- Al cerrar: `status: cerrada`, mover a `03-completadas/`; hallazgos
  permanentes → promoción a canon/ADR/ficha (campo `promociones`).

## Reglas

- Solo lectura por defecto: ninguna automatización modifica código ni
  documentación; reporta. La corrección la hace el agente o humano.
- Sin red ni servicios externos salvo que la especificación lo exija
  (rutas-vivas y humo-integral sí levantan el proyecto).
- Toda implementación nueva se registra en `35-herramientas/autorizadas/`
  antes de ejecutarse por primera vez.
- Espejo: lo que se agregue aquí en backend se replica en frontend y
  viceversa (ver `scripts/verificar-paridad.py`).
