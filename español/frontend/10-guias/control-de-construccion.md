# Control de construcción — hacer cumplir cómo se construye sobre la aplicación

uxyngraphar no solo documenta: `scripts/controlar.py` es una **puerta** que revisa cada cambio (commit o PR) contra las reglas del protocolo. Sirve en cualquier aplicación y pila; lo que cambia por proyecto es `docs/uxyngraphar.config.json`.

## Qué controla

| Control | Regla | Qué detecta | Nivel por defecto |
|---------|-------|-------------|-------------------|
| `lineas` | R-19 | Código tocado con más de `limite_lineas` (350) | aviso |
| `instruccion` | R-03 | Código tocado sin instrucción cuyo `anclas_codigo` lo cubra | aviso |
| `secretos` | R-12 | Archivos de llaves/`.env` o credenciales en líneas añadidas (también en `docs/` y `.md`) | **bloqueante** |
| `nucleo` | R-20 | Núcleo del pack alterado (delega en `verificar-nucleo.py`) | **bloqueante** |
| `espejo` | R-08 | `espejo_actualizar` declarado que no cambió en el diff | aviso |
| `idioma` | R-22 | Identificadores y archivos nuevos del producto con caracteres no-ASCII (fiable); palabras, comentarios y textos en español (heurístico: siempre aviso). Nunca revisa `docs/` | aviso |
| `commits` | R-22 | Asunto de commit fuera de Conventional Commits o en español; nombre de rama fuera de `tipo/alcance-descripcion` | aviso |
| `memoria` | R-24 | Cambios en `95-memoria/` hechos fuera de `memoria.py`: una memoria editada, borrada o añadida a mano (catálogo y huellas no cuadran) | **bloqueante** |
| `reglas_proyecto` | — (reglas del proyecto, no del núcleo) | Archivos de código del cambio que incumplen la `comprobacion_*` de una regla activa de `96-reglas-proyecto/` (las de nivel aviso solo avisan) sin excepción aprobada; excepciones en instrucciones sin aprobar (o prohibidas por la configuración); reglas `RP-*`/`EX-*` cambiadas sin una instrucción aprobada que las ancle. Protocolo: `96-reglas-proyecto/_PROTOCOLO.md` | **bloqueante** |

Niveles: `bloqueante` (exit 1), `aviso` (se muestra), `apagado`. Con `--estricto` todo aviso bloquea. Proyecto nuevo: instala con `instalar-pack.py --estricto`. Proyecto existente: deja `aviso` y sube de nivel por control cuando el inventario esté al día.

## Configuración (`docs/uxyngraphar.config.json`)

Se genera sola al instalar (detecta pila por `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `pubspec.yaml`, `*.csproj`…). Es clase **P**: el proyecto la edita y las actualizaciones no la pisan.

```json
{
  "version": 1, "rol": "servidor", "pila": ["python"],
  "codigo": {"raices": ["src"], "extensiones": [".py"], "excluir": ["migrations/**", "*.generated.*"]},
  "limite_lineas": 350,
  "exenciones_lineas": ["src/legado/**"],
  "niveles": {"lineas": "aviso", "instruccion": "aviso", "secretos": "bloqueante", "nucleo": "bloqueante", "espejo": "aviso", "idioma": "aviso", "commits": "aviso"},
  "idioma": {"artefactos": "en", "conversacion": "espejo", "glosario": "00-nucleo/glosario-dominio.md", "excluir": ["**/generated/**"],
             "legacy": ["src/legado/**"], "locales": ["**/locales/**", "*.po"], "commits": "conventional", "ramas": ""}
}
```

- `codigo.raices`/`extensiones` definen qué es «código del producto». Vacío = se usan extensiones comunes.
- `exenciones_lineas`: globs permitidos por encima del límite; cada exención debe tener una decisión que la justifique.
- `idioma`: parámetros de R-22 (idioma de artefactos y de conversación, glosario, rutas excluidas, legacy, locales, commits y ramas). Detalle de cada clave: [politica-idioma.md](../00-nucleo/politica-idioma.md) §9.
- Un archivo ilegible o con valores inválidos no rompe nada: se usan los valores por defecto y `doctor.py` lo reporta.
- Referencia de todas las secciones y reglas para añadir otras: [configuracion-uxyngraphar.md](configuracion-uxyngraphar.md).

## Dónde corre

- **Local:** el gancho `pre-commit` (`instalar-ganchos.py`) ejecuta `controlar.py --staged`; `commit-msg` ejecuta `controlar.py --mensaje` (R-22); `pre-push` ejecuta `--base`.
- **CI (la barrera real):** `python3 docs/scripts/controlar.py --base origin/main` en el pipeline del PR (también revisa los asuntos de los commits del PR y el nombre de la rama). Los ganchos locales se pueden saltar; el CI no. `instalar-pack.py --proteger` (y el asistente) generan `.github/workflows/uxyngraphar.yml` en la **raíz del repo** (GitHub no lee workflows de subcarpetas); falta marcarlo como check requerido en la protección de rama. Ver [ci-validacion-documentacion.md](ci-validacion-documentacion.md).
- **La configuración no la cambia un agente:** `docs/uxyngraphar.config.json` fija los niveles, las exenciones y `secretos_permitir`; está en las reglas `deny` y en `CODEOWNERS`, y la puerta avisa en cualquier cambio que la toque. Relajarla es decisión del propietario.
- **Revisión:** `doctor.py` incluye el chequeo `control` (config legible, pila detectada, controles apagados).

## Límites honestos

Detecta patrones, no intención: los secretos se buscan por formato (claves conocidas y asignaciones literales), el límite de líneas cuenta líneas físicas y la cobertura de anclas compara rutas. Un humano sigue revisando el diseño. Un agente con shell puede evitar un gancho local, por eso el CI y `CODEOWNERS` (ver [actualizar-nucleo.md](actualizar-nucleo.md)) son obligatorios para control real.

## Credenciales (R-12): capas de protección

| Capa | Qué hace |
|------|----------|
| `controlar.py` (commit/PR) | Bloquea archivos `.env*`, `*.pem`, `*.key`, `id_rsa`, `credentials.json`, `*.tfstate`… (salvo `.env.example`, `*.pub`) y credenciales por formato (AWS, GitHub, Slack, Stripe, Google, JWT, claves privadas, URLs `usuario:clave@host`, asignaciones literales). Los hallazgos salen **enmascarados**. |
| `.gitignore` | `instalar-pack.py` y `doctor.py --fix` añaden los patrones de credenciales. |
| Reglas `deny` (`--proteger`) | El agente no puede leer ni escribir `.env`, llaves, `~/.ssh`, `~/.aws`, `~/.kube`… |
| `escanear-secretos.py` | Auditoría del árbol y, con `--historia`, de **todo el historial**; úsalo en CI y al adoptar un repositorio existente. |
| `doctor.py` | Chequeo `secretos`: ERROR si hay credenciales en el árbol, WARN si faltan las reglas `deny`. |

Un fixture de pruebas con forma de credencial se exime con la marca `uxyngraphar:permitir-secreto` en la misma línea, o por ruta con `secretos_permitir` en `uxyngraphar.config.json`. **Si una credencial ya se subió, borrar el commit no basta: rótala.** Limitación: la detección es por formato; un secreto sin forma reconocible (una contraseña corta sin etiqueta) no se detecta. Las reglas `deny` no frenan a un agente con shell (`cat .env`), por eso la barrera real es el CI + rotación + no tener secretos en el equipo del agente.
