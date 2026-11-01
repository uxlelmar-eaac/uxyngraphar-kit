# El panel: todo desde un solo comando

```bash
uxyngraphar
```

Es el único comando que necesitas. Abre el panel en tu navegador, **solo en tu equipo** (no es la web pública de uxyngraphar.com). Desde ahí se instala, configura y actualiza todo; cada cambio enseña antes qué hará y, si toca archivos, guarda una copia de seguridad que puedes restaurar desde el propio panel. `uxyngraphar panel` hace lo mismo.

Si lo ejecuta un agente o el CI (o no hay escritorio), no abre nada: imprime la ayuda. El panel solo cambia cosas con una persona delante.

## Dónde está cada cosa

| Quieres… | En el panel |
|----------|-------------|
| Instalar uxyngraphar en un proyecto | **Mis proyectos** → «Instalar uxyngraphar en un proyecto nuevo» |
| Registrar un proyecto que ya lo tiene | **Mis proyectos** → «Añadir» (o «Examinar…») |
| Actualizar un proyecto, o todos | **Mis proyectos** → «Actualizar» / «Actualizar todos» |
| Ver si un proyecto está sano y arreglar lo seguro | **Proyecto → Salud** → «Arreglar» |
| Aprobar o rechazar una instrucción, mejora, EVO o propuesta | **Proyecto → Pendientes** → «Leer y decidir» → ver el cambio → «Confirmar» |
| Cambiar la configuración (`uxyngraphar.config.json`) | **Proyecto → Configuración** |
| Colaborar Sí/No y ver qué saldría exactamente | **Proyecto → Configuración → Colaborar** |
| Mover el pack de `docs/` a `uxyngraphar/` | **Proyecto → Configuración → Carpeta del sistema** |
| Deshacer un cambio | **Proyecto → Copias de seguridad** → «Ver y restaurar» |
| Buscar, ver, recuperar o purgar en la memoria | **Proyecto → Memoria** |
| Ganchos de git y quién aprueba el núcleo (CODEOWNERS) | **Proyecto → Protecciones** |
| Reglas del equipo y archivar fichas antiguas | **Proyecto → Reglas y fichas** |
| Tus preferencias para proyectos nuevos | **Plantilla** |
| Actualizar la herramienta | Arriba a la derecha, «Actualizar a X» (el panel se reabre solo en la versión nueva) |
| Volver a una versión anterior | **Sistema → Versiones guardadas** |
| Añadir o quitar `uxyngraphar` del PATH | **Sistema → El comando uxyngraphar en tu terminal** |
| Quitar proyectos que ya no existen | **Sistema → Limpiar** |
| Desinstalar la herramienta | **Sistema → Desinstalar** (escribe «desinstalar» para confirmar) |

La pestaña **Atajos y comandos** repite esta tabla con un botón «Ir» y, plegados, los comandos de terminal para usuarios avanzados, CI y agentes ([../05-comandos/referencia-cli.md](../05-comandos/referencia-cli.md)).

## Al actualizar la herramienta

Tras «Actualizar a X» (o «Usar esta» en una versión 1.2.0 o posterior), el panel arranca el de la versión nueva y la página se va a él sola. Ese panel queda en segundo plano: ciérralo con «Cerrar» (si lo dejas abierto sin usarlo, se cierra solo a las 4 horas). Tus proyectos no cambian hasta que los actualizas en **Mis proyectos**.

## Al desinstalar

El panel borra la herramienta, el comando y la línea del PATH, y se cierra solo (su programa ya no existe). La terminal donde lo abriste puede mostrar un aviso (en Windows, «no se encuentra el archivo por lotes»): es normal. Tus proyectos conservan su `uxyngraphar/`.

## Elegir carpetas

Cada botón **Examinar…** abre un explorador de carpetas dentro de la página, sin ventanas del sistema. Muestra la ruta actual (cada parte se puede pulsar), un cuadro para escribir una ruta e ir directo, atajos (carpeta personal, Escritorio, Documentos, proyectos registrados y unidades en Windows) y las subcarpetas con las etiquetas «git» y «uxyngraphar». «Usar esta carpeta» la pone en el cuadro; «Cancelar» o `Esc` cierra sin cambiar nada. Solo lee nombres de carpetas: no abre ni modifica archivos.
