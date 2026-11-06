---
id: {{id}}
status: {{status}}
source: human
tipo: solo-docs
created: {{fecha}}
approved_at: null
executed_at: null
lectura_minima: []
anclas_codigo: []
documentos: []
---

# {{titulo}}

<!-- Solo documentación: `anclas_codigo` queda vacío y ningún archivo de código cambia.
     `documentos`: lo que se escribirá (fichas de otros paquetes, guías, espejo). -->

## Objetivo
Una frase.

## Documentos a tocar
- `…` — qué cambia

## Plan
1. Leer `lectura_minima`.
2. Editar `documentos`.
3. Cerrar con el resultado.

## Criterios de aceptación
- [ ] Cero archivos de código modificados
- [ ] Documentos alineados con el código actual

## Resultado (al cerrar)
- …

## Decisión (persona)
- Aprobar: `python3 uxyngraphar/paquetes/instrucciones-aprobadas/scripts/ciclo.py aprobar {{id}} --humano`
- Cancelar: `python3 uxyngraphar/paquetes/instrucciones-aprobadas/scripts/comun/fichas.py estado {{id}} cancelled`
