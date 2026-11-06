# Contratos entre repositorios

Activado con «usa el paquete contratos-entre-repositorios» / «sigue el protocolo contratos de api» o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/contratos-entre-repositorios/scripts`.

Para proyectos con un repo que sirve una API y otros que la consumen (servidor y cliente, o varios servicios).

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo) y, si el cambio cruza repos, `uxyngraphar/paquetes/contratos-entre-repositorios/docs/sincronizar.md`.
3. Al consumir o publicar una ruta de otro repo: `python3 $S/comun/fichas.py nueva contrato --slug <slug>`; rellena `id_compartido`, `rol`, `method`, `path`, `version`, `proveedor` y `ficha_proveedor`.
4. Regenera el registro: `python3 $S/contratos.py registro`. Si el repo hermano está al lado (`otros_repos` en ajustes): `python3 $S/contratos.py comparar`.
5. En el consumidor, lado técnico: `uxyngraphar/paquetes/contratos-entre-repositorios/docs/contratos-api.md`.
6. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-contratos.py`.

Persona: `vigente` y `retirado` (`fichas.py estado CON-… vigente --humano`); `otros_repos` en `uxyngraphar/trabajo/contratos-entre-repositorios/ajustes.json` (p. ej. `["../mi-api"]`).

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Un id compartido, el mismo en todos los repos** (`modulo.recurso.accion`). Se cita en áreas, espejo e instrucciones; no se renombra (contrato nuevo y retirada del anterior).
2. **No duplicar:** el consumidor cita la ficha del proveedor; nunca copia su ficha ni su OpenAPI.
3. **Proveedor primero:** no cierres un cambio del consumidor que depende de un contrato que el proveedor aún no fusionó.
4. **Cambios incompatibles** con nueva `version` y convivencia; la anterior pasa a `deprecado`.
5. **Repo aislado:** no abras el otro repo salvo para `comparar` o si el pedido lo pide.
6. **Solo una persona** marca `vigente` o `retirado`.
