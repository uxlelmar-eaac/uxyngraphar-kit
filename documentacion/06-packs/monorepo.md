# Monorepo y multi-repo

## Un solo repo, ambos packs

Marca **explícitamente** `--mismo-repo` y las subcarpetas:

```bash
uxyngraphar instalar "$MONOREPO" \
  --pack ambos --mismo-repo \
  --sub-servidor apps/api --sub-cliente apps/web \
  --si --colaborar no
```

Cada árbol tendrá su `docs/.uxyngraphar.lock`. El doctor se ejecuta **por cada** `docs/`:

```bash
python3 apps/api/docs/scripts/doctor.py
python3 apps/web/docs/scripts/doctor.py
```

### Peligro del default con `--si`

Si pasas `--pack ambos --si` **sin** `--proyecto2` ni flags de subcarpeta, el asistente de consola suele asumir **mismo repo** y `apps/api` + `apps/web`. Si tu layout es otro, indica `--sub-servidor` / `--sub-cliente` (usa `""` para la raíz).

## Dos repos (API + UI)

```bash
python3 español/instalar.py \
  --proyecto "$BACKEND" --proyecto2 "$FRONTEND" \
  --pack ambos --si --colaborar no
```

Mantén alineado `registro-ids-compartidos` entre ambos.

## Guías del pack (tras instalar)

- `docs/10-guias/elegir-pack.md`
- `docs/10-guias/sync-multi-repo.md`
- `docs/10-guias/monorepo-docs-fusionados.md`
