# Seguridad

## Reportar vulnerabilidades

Si encuentras un problema de seguridad en el **kit uxyngraphar** (instalador, scripts, panel local, publicación de releases), **no** abras un issue público con detalles explotables.

1. Usa [GitHub Security Advisories](https://github.com/uxlelmar-eaac/uxyngraphar-kit/security/advisories/new) si está habilitado, **o**
2. Contacta al mantenedor: **uxleleaac / uxlelmar**.

Incluye: descripción, pasos para reproducir, impacto estimado y, si puedes, una corrección sugerida.

## Verificar lo que instalas

Cada release lleva una **atestación de procedencia** de GitHub (`actions/attest-build-provenance`) para el zip, el instalador y `SHA256SUMS`. La firma la hace el propio workflow de publicación con la identidad OIDC de GitHub Actions: no hay ninguna clave privada que guardar ni rotar, y nadie puede firmar a mano un archivo como si lo hubiera construido el workflow.

Qué comprueba el instalador:

- Siempre: la huella SHA256 del zip frente a `SHA256SUMS` y la de cada archivo frente a `ARCHIVOS.sha256`. Eso garantiza la **integridad**, pero no la **autenticidad**: quien pudiera sustituir los archivos de la release podría sustituir también las sumas.
- Si tienes la CLI de GitHub (`gh`) con sesión iniciada: además, `gh attestation verify` del zip contra `uxlelmar-eaac/uxyngraphar-kit`. Si la atestación no corresponde, no instala nada.
- Sin `gh`, sin sesión o sin red: avisa y sigue solo con la huella SHA256. `--sin-firma` omite la comprobación a propósito.

### Vía verificable (recomendada en equipos con datos sensibles)

La instalación de una línea (`curl … | python3 -`) ejecuta el instalador **antes** de que nada lo haya verificado. Para verificarlo primero:

```bash
curl -fsSLO https://github.com/uxlelmar-eaac/uxyngraphar-kit/releases/latest/download/instalar-uxyngraphar.py
gh attestation verify instalar-uxyngraphar.py --repo uxlelmar-eaac/uxyngraphar-kit
python3 instalar-uxyngraphar.py
```

En Windows (PowerShell): `iwr <misma URL> -OutFile instalar-uxyngraphar.py`, el mismo `gh attestation verify` y `py instalar-uxyngraphar.py`. Después, el instalador comprueba el zip por su cuenta.

Las Actions de los workflows van fijadas por SHA completo y Dependabot propone las actualizaciones; el zip es reproducible (fecha fija, orden estable y permisos normalizados), así que cualquiera puede regenerar su huella desde la etiqueta con `python3 español/motor/distribucion/publicar.py`.
