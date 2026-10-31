# Plantilla — promover herramienta desde propuesta

Checklist humano para mover una ficha de `35-herramientas/propuestas/` a `autorizadas/`.

## Cuándo usar

La IA creó una propuesta en `propuestas/` y el humano decide **promoverla** a herramienta ejecutable sin instrucción nueva.

## Checklist

1. [ ] Leer la propuesta en `propuestas/01-pendientes/YYYY-MM-DD/<slug>.md` y validar alcance, seguridad y anclas.
2. [ ] Copiar a `autorizadas/<id>.md` desde [_PLANTILLA-autorizada.md](_PLANTILLA-autorizada.md).
3. [ ] Ajustar frontmatter:
   - `status: authorized`
   - `authorized_by: <humano>`
   - `authorized_at: YYYY-MM-DD`
   - `alcance_permitido:` descripción clara y acotada
   - `anclas_codigo` y `lectura_minima` si aplica
4. [ ] Añadir fila en [autorizadas/INDICE.md](autorizadas/INDICE.md).
5. [ ] Mover propuesta original a `propuestas/05-canceladas/` **o** marcar `status: rejected` y conservarla fuera de `01-pendientes/` (R-17).
6. [ ] Comunicar al equipo: id, alcance y excepción (sin instrucción nueva).

## No hacer

- Promover sin revisar secretos o comandos destructivos.
- Dejar duplicado activo en `propuestas/` y `autorizadas/`.
- Ejecutar propuesta antes de completar el checklist.

## Referencias

- [herramientas-autorizadas-vs-propuestas.md](../10-guias/herramientas-autorizadas-vs-propuestas.md)
- [_PROTOCOLO.md](_PROTOCOLO.md)
