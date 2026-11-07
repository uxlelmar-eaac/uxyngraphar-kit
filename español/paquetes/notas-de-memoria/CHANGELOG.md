# Cambios

## 1.0.0

- Nace de dividir `memoria-e-historial` (1.1.0): se queda con las notas de memoria (`conocimiento-del-proyecto-perdido`, `memoria-leida-sin-pedido`, `notas-caducadas-tratadas-como-vigentes`). El archivo histórico pasa a `documentos-archivados`.
- Misma ficha `nota` (prefijo `MEM`, carpeta `memoria/`, status `vigente`/`archivada`, misma plantilla); el trabajo vive en `uxyngraphar/trabajo/notas-de-memoria/memoria/`.
- Fases `buscar-en-memoria` y `guardar-nota`; skills `buscar-en-notas`, `registrar-nota` y `archivar-nota-caducada`.
- `memoria.py buscar <texto>` pasa a `notas.py buscar <texto>`, con la misma salida. Sin `protegidos` ni `fuera_de_ia`.
- Pruebas propias en `pruebas/test_notas.py`.
