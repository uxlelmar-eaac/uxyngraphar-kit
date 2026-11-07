# Caso: estado de expedientes en un módulo escrito a medias en español

## Pedido

«Añade al expediente un campo con la fecha de resolución y muestra "Expediente resuelto" cuando la tenga.» Proyecto TypeScript; el módulo `src/expedientes/` lo empezó otra persona en español. El glosario tiene una fila: `expediente` (case file, dominio).

## Recorrido

**diagnosticar.** `revisar-idioma` sobre los archivos que se van a tocar:

```
python3 $P/scripts/idiomas.py src/expedientes/expediente-service.ts src/expedientes/validación.ts
src/expedientes/validación.ts: nombre de archivo no ASCII; tradúcelo al inglés (referencia/idioma.md)
idiomas-del-codigo: 2 archivos revisados, 1 problemas
```

`validación.ts` es heredado: se anota. `consultar-glosario`:

```
python3 $P/scripts/glosario.py terminos
expediente
```

«Expediente» puede quedarse; «fecha de resolución» no está en el glosario y tiene traducción precisa: `resolutionDate`. El servicio tiene funciones `obtenerExpediente()` y un log `console.log("expediente guardado")`: código antiguo en otro idioma, no se renombra de paso (sus usos salen del pedido).

**escribir-codigo.**

- Campo nuevo `resolutionDate: Date | null` en `Expediente` y función `isExpedienteResolved(expediente)`: inglés, con el término del glosario en ASCII y el casing del código.
- El texto «Expediente resuelto» no va en la lógica: clave `expediente.status.resolved` en `locales/es.json` (y `"Case closed"` en `locales/en.json`).
- Log nuevo en inglés: `logger.info("expediente resolution date set", { expedienteId })`.

**verificar.**

```
python3 $P/scripts/idiomas.py src/expedientes/expediente-service.ts src/expedientes/validación.ts
src/expedientes/validación.ts: nombre de archivo no ASCII; tradúcelo al inglés (referencia/idioma.md)
idiomas-del-codigo: 2 archivos revisados, 1 problemas
```

El único problema es el heredado de `diagnosticar`. El repaso del diff no encuentra identificadores, comentarios ni logs nuevos fuera del inglés.

## Resultado

- Todo lo nuevo en inglés ASCII salvo `expediente`, que está en el glosario.
- El texto para el usuario en los archivos de locale.
- Al cerrar se mencionan `validación.ts`, `obtenerExpediente()` y el log en español como heredados (o se registran en `deuda-y-mejoras` si está instalado). Ningún término añadido al glosario.
