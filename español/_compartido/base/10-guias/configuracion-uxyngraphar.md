# Configuración del proyecto: `docs/uxyngraphar.config.json`

Cada proyecto tiene **un archivo propio** donde fija su forma de trabajo con uxyngraphar: qué es código del producto, qué controles bloquean o solo avisan, idioma, commits, ramas, copias de seguridad… Las herramientas (`controlar.py`, `doctor.py`, `respaldos.py`, el instalador) leen **solo** este archivo.

| | |
|---|---|
| Ruta | `docs/uxyngraphar.config.json` (en un monorepo, dentro de la carpeta `docs` de cada pack) |
| Lo crea | El instalador, una vez, detectando la pila del repo. Si ya existe, no lo toca. |
| Lo edita | El propietario del proyecto (clase **P**). Las actualizaciones del pack **nunca** lo pisan. |
| No lo edita | Un agente: está en las reglas `deny` y en `CODEOWNERS`, y la puerta avisa si un cambio lo toca. |
| Ficha humana | [`00-nucleo/configuracion-proyecto.md`](../00-nucleo/configuracion-proyecto.md): identidad, rutas y convenciones del equipo en prosa. El JSON es lo que la máquina hace cumplir. |

## Cómo se lee

1. Se parte de los **valores por defecto** (`por_defecto()` en `scripts/control/uxyngraphar_config.py`).
2. Se **fusiona** encima lo que el proyecto escribió (sección a sección; las claves que faltan conservan su valor por defecto).
3. Se **valida**. Un archivo ausente, ilegible o con valores inválidos no rompe nada: se usan los valores por defecto y `doctor.py` lo reporta.

Por eso basta con escribir **solo lo que el proyecto cambia**.

## Cómo se edita: el panel

Con la herramienta instalada, `uxyngraphar panel` abre en tu navegador (solo en tu equipo) un panel con tres partes:

- **Mis proyectos:** los proyectos registrados en este equipo, con su versión y su salud; añadir, quitar, actualizar o instalar en uno nuevo.
- **Configuración del proyecto:** un formulario con cada sección de esta tabla, explicada. Valida mientras eliges, enseña qué cambia (también línea a línea) antes de guardar, no pisa el archivo si alguien lo cambió mientras tanto y deja una copia en `.uxyngraphar-respaldo/` (se restaura con `respaldos.py restaurar`). «Colaborar» Sí/No pasa por `feedback.py activar`/`revocar`; los campos de consentimiento, `version`, `pila` e `idioma.artefactos` no se editan desde ahí. Con `cambios_reglas: solo_humano` añade las reglas deny del agente.
- **Plantilla y sistema:** versión de la herramienta y aviso si hay otra publicada, y la **plantilla** de este equipo (`plantilla-config.json` en la carpeta de la herramienta): tus valores preferidos de `niveles`, `limite_lineas`, `idioma.conversacion`/`commits`/`ramas`, `respaldos`, `memoria`, `reglas_proyecto` y `feedback.ocultar`. Se aplica sola al **instalar** un proyecto nuevo; en los existentes solo si lo pides, viendo antes qué cambia en cada uno. La plantilla nunca manda sobre este archivo: lo que vale es lo que está aquí (va en git, así tu equipo y el CI ven lo mismo).

El panel solo lo usa una persona: si detecta CI o un agente (`CLAUDECODE`, `UXYNGRAPHAR_AGENTE`…) no cambia nada. El comando de instalación de una línea lo abre al terminar, en modo bienvenida.

Ver la configuración efectiva y sus problemas en texto:

```bash
uxyngraphar configuracion            # con la herramienta instalada (desde la carpeta del proyecto)
python3 docs/scripts/doctor.py       # chequeo «control» (En Windows: py -3 en lugar de python3.)
```

## Secciones

| Clave | Por defecto | Qué decide el proyecto |
|---|---|---|
| `version` | `1` | Versión del **formato** del archivo. No se toca a mano (ver «Cómo crece»). |
| `rol` | detectado | `servidor` o `cliente`. |
| `pila` | detectada | Pilas encontradas (`python`, `node`, `go`, `dotnet`…). Informativo. |
| `codigo.raices` | detectadas | Carpetas con código del producto. Vacío = todo el repo. |
| `codigo.extensiones` | detectadas | Extensiones que cuentan como código. Vacío = extensiones comunes. |
| `codigo.excluir` | `node_modules/**`, `dist/**`, `*.lock`… | Rutas que nunca son código del producto. |
| `limite_lineas` | `350` | Máximo de líneas por archivo de código (R-19). Entero ≥ 50. |
| `exenciones_lineas` | `[]` | Globs que pueden superar el límite; cada uno con su decisión en `20-decisiones/`. |
| `secretos_permitir` | `[]` | Rutas de fixtures con forma de credencial. Alternativa por línea: marca `uxyngraphar:permitir-secreto`. |
| `niveles.<control>` | ver abajo | `bloqueante`, `aviso` o `apagado` para cada control de la puerta. |
| `idioma` | R-22 | Idioma de artefactos y de conversación, glosario, legacy, locales, commits y ramas. Detalle: [politica-idioma.md](../00-nucleo/politica-idioma.md) §9. |
| `respaldos` | 30 días, mínimo 3, limpieza automática | Cuánto se guardan las copias de seguridad. Detalle: [respaldos.md](respaldos.md). |
| `memoria.archivadas_a_memoria_dias` | `180` | Días en `04-archivadas` antes de que `depurar` proponga pasar la ficha a la memoria (R-24). |
| `memoria.listas_a_memoria_dias` | `30` | Días en `06-listas-para-eliminar` antes de proponerlo. |
| `memoria.permitir_purgar` | `true` | `false` impide el borrado definitivo (`memoria.py purgar`). Detalle: [memoria.md](memoria.md). |
| `reglas_proyecto` | `excepciones: en_instruccion`, `cambios_reglas: instruccion_aprobada` | Reglas del proyecto (`96-reglas-proyecto/`). `excepciones`: `en_instruccion` (declarada en la instrucción, aprobada al aprobarla), `ficha_aparte` (además una ficha `EX-*.md` aprobada por una persona) o `prohibidas`. `cambios_reglas`: `instruccion_aprobada` (el agente crea o cambia reglas solo con una instrucción aprobada que las ancle) o `solo_humano` (reglas deny: el agente no puede tocarlas). El control se gradúa con `niveles.reglas_proyecto` (por defecto `bloqueante`). |
| `feedback` | apagado | Envío voluntario de sugerencias (R-25): `activo`, `url`, `consentimiento`, `id_instalacion`, `respondido` (`""`, `"si"`, `"no"`), `respondido_en` y `origen` (**no se editan a mano**: los escriben la pregunta del instalador/actualizador, `feedback.py activar` y `revocar`) y `ocultar` (nombres que se quitan antes de enviar: cliente, producto, empresa; este sí lo editas tú); `activo: true` sin consentimiento es inválido. Detalle: [envio-sugerencias.md](envio-sugerencias.md). |

Controles y nivel por defecto: `lineas` aviso · `instruccion` aviso · `secretos` bloqueante · `nucleo` bloqueante · `espejo` aviso · `idioma` aviso · `commits` aviso · `memoria` bloqueante · `reglas_proyecto` bloqueante. Qué revisa cada uno: [control-de-construccion.md](control-de-construccion.md).

Ejemplo mínimo (solo lo que cambia respecto a los valores por defecto):

```json
{
  "niveles": {"lineas": "bloqueante", "idioma": "bloqueante"},
  "exenciones_lineas": ["src/legacy/**"],
  "idioma": {"conversacion": "es", "legacy": ["src/legacy/**"]},
  "respaldos": {"conservar_dias": 60}
}
```

## Cómo crece este archivo

El archivo está pensado para ir ganando secciones a medida que uxyngraphar permita a cada proyecto decidir más cosas sobre su forma de trabajo. Toda sección nueva se añade **en el repositorio fuente de uxyngraphar** (R-20), con estas reglas:

1. **Valor por defecto que no cambia nada.** La sección nueva entra en `por_defecto()` con el comportamiento que había antes de existir. Así ningún proyecto tiene que editar su archivo al actualizar: la fusión le da la sección nueva sola.
2. **Validación.** `validar()` comprueba tipos y valores, con un mensaje que diga qué poner.
3. **Prueba** en `scripts/control/test_control.py` (valor por defecto, valor válido, valor inválido).
4. **Documentación** en la tabla de esta guía y, si la sección es de una regla, en el documento de esa regla.
5. **Versión del pack:** sección nueva compatible = `MENOR` en `CHANGELOG.md` y `VERSION.md`.
6. **Sin romper archivos existentes.** Renombrar o quitar una clave, o cambiar su significado, es `MAYOR`: sube `version` del formato y la actualización del pack migra el archivo del proyecto (con respaldo) en lugar de dejar valores huérfanos.

Una propuesta de sección nueva hecha desde un proyecto se registra como ficha `EVO-*` en `46-evolucion-documentacion/` (no se edita el núcleo del proyecto).
