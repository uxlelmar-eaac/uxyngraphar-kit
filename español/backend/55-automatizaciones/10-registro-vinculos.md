---
id: auto.10.registro-vinculos
stack: [servidor]
---

# 10: registro-vinculos

## Fuente

`50-sistema-integral/` (cada `.md` espejo es una entrada) y el código del
proyecto (cada función pública lleva su línea de vínculo).

## Idea

Un registro `documentation` **generado** desde el espejo, con espacios de
nombres por módulo + archivo + función (`modUsers.authService.findall`).
Arriba de cada función pública va una sola línea con su referencia. El
registro nunca se edita a mano (lleva marca `GENERADO — no editar`) y se
versiona para que cada PR muestre qué vínculos cambiaron junto al código.

## Valida

Que cada vínculo resuelve a una entrada real, que cada entrada tiene
contenido mínimo y al menos una referencia, y que la cobertura no baja.

## Procedimiento

1. Regenerar el registro desde `50-sistema-integral` (un `.md` espejo →
   una entrada `modulo.archivo.funcion`).
2. Extraer del código todas las líneas de vínculo (incluyen hash corto
   de la firma: `findall__a3f9`).
3. Verificar en ambas direcciones: vínculo → entrada y entrada → vínculo.
4. Verificar contenido mínimo de cada entrada (`hace`, `entrada/salida`).
5. Calcular cobertura (% funciones públicas con vínculo válido) y
   compararla contra `registro-cobertura-espejo.md`.

## Aceptación

- [ ] Cero vínculos a entradas inexistentes (archivo y línea reportados).
- [ ] Cero entradas sin contenido mínimo (se marcan incompletas, no válidas).
- [ ] Cero entradas con cero referencias fuera de su periodo de gracia.
- [ ] Cero funciones públicas sin vínculo, salvo exclusión por convención
  (privadas, p. ej. prefijo `_`) o excepción temporal vigente.
- [ ] La cobertura del PR es mayor o igual a la registrada.
- [ ] Cero colisiones: el namespace incluye módulo + archivo.
- [ ] Hash de firma vigente: si cambió la función sin actualizar la doc,
  el vínculo falla en vez de apuntar a lo equivocado.

## Excepciones temporales

El código legacy entra con excepción registrada como decisión activa en
`20-decisiones/` **con fecha de caducidad**. Vencida la fecha, la
excepción se vuelve falla. Nada queda exento para siempre. En modo
adopción (primeros 30 días en un proyecto existente) las verificaciones
corren en aviso; después pasan a bloqueantes.

## Autofix

Cuando falta una línea, la herramienta **propone** la referencia exacta
pero no la escribe. El humano o el agente la aprueba. Cero cambios
silenciosos.

## Salida

`vínculo o entrada | estado (válido/incompleto/huérfano/roto) | detalle` +
cobertura total del proyecto.
