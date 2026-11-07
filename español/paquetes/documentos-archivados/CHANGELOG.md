# Cambios

## 1.0.0

- Nace de dividir `memoria-e-historial` (1.1.0): se queda con el archivo histórico (`archivo-historico-alterado`, `documentos-retirados-sin-archivar`). Las notas de memoria pasan a `notas-de-memoria`.
- El archivo vive en `uxyngraphar/trabajo/documentos-archivados/archivo/<AAAA-MM-DD>/`, con `protegidos` y `fuera_de_ia` = `archivo/**`.
- Fase `archivar-documento` y skill `preparar-archivado`.
- Plantilla nueva `plantillas/aviso-de-retirada.md` para dejar una referencia en lugar del original.
- `memoria.py archivar <ruta> --humano` pasa a `archivo.py archivar <ruta> --humano` y `memoria.py buscar <texto> --archivo --humano` a `archivo.py buscar <texto> --humano`, con las mismas salidas.
- Pruebas propias en `pruebas/test_archivo.py`.
