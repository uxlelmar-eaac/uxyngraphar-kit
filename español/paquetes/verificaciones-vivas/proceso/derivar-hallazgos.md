---
fase: derivar-hallazgos
resuelve: [fichas-desalineadas-del-codigo, referencias-rotas, decisiones-incumplidas, manuales-sin-verificar]
skills: []
---

# Fase: derivar hallazgos

## Objetivo

Que cada hallazgo tenga un camino de resolución propuesto, sin que el agente lo resuelva por su cuenta.

## Entradas

- La tabla de hallazgos de `informar`.
- Los paquetes instalados que pueden recogerlos.

## Pasos

1. Propón para cada grupo de hallazgos su flujo:
   - Ruta o página sin ficha → crear la ficha con `rutas-de-api` o `paginas-de-interfaz`.
   - Ficha activa sin código, ancla rota o id colgante → actualizar o retirar la ficha en su paquete.
   - Decisión incumplida → corregir el código con una instrucción aprobada, o revisar la ADR con `decisiones-de-arquitectura`.
   - Manual caducado o con rutas inexistentes → reverificarlo con `manuales-operativos`.
   - Humo fallido → arreglo con instrucción aprobada.
2. Lo que no se vaya a corregir ahora, propón registrarlo en `deuda-y-mejoras` si está instalado.
3. Con `auditorias-tecnicas` instalado, la auditoría generada permite promover hallazgos desde ella.
4. Espera la decisión de la persona: ningún flujo se arranca sin su visto bueno (límite 5).
5. Ejecuta la verificación del paquete: `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- Cada hallazgo tiene un flujo propuesto y la persona sabe qué tiene que decidir.
- `verificar.py` sin errores.
