# Caso: cliente de Stripe con una clave pegada y un `.env` en el repositorio

## Pedido

«Conecta el módulo de pagos con Stripe; la clave está en el `.env`.» Proyecto TypeScript con git; ajustes por defecto.

## Recorrido

**diagnosticar.** El agente no abre `.env` (límite 2). `escanear-secretos` sobre lo que irá al commit:

```
python3 $P/scripts/secretos.py --git
.env: archivo de secretos (por nombre); no debe versionarse
secretos: 13 archivos revisados, 1 hallazgos
```

El `.env` existe y no está ignorado: hallazgo heredado, se avisa a la persona. La variable que necesita el cambio será `STRIPE_SECRET_KEY`.

**implementar.** Un borrador previo de otra sesión había dejado la clave en el cliente:

```
python3 $P/scripts/secretos.py src/payments
src/payments/stripe-client.ts:1: clave Stripe (sk_l…(32 car.))
secretos: 2 archivos revisados, 1 hallazgos
```

Es una clave `sk_live_`: parece real, así que se pasa a **atender-incidente**.

**atender-secreto-expuesto** (skill). Sin copiar el valor, `git log --oneline -- src/payments/stripe-client.ts` muestra que el archivo no se ha versionado nunca. Aviso a la persona: «`src/payments/stripe-client.ts:1`, clave Stripe `sk_l…(32 car.)`, no está en el historial ni en el remoto; conviene revocarla igualmente si salió de este equipo». Con **sustituir-por-variable-de-entorno**:

```ts
// src/payments/stripe-client.ts
const secretKey = process.env.STRIPE_SECRET_KEY;
if (!secretKey) throw new Error("STRIPE_SECRET_KEY is not set");
export const stripeClient = new Stripe(secretKey);
```

y en `.env.example`: `STRIPE_SECRET_KEY=<STRIPE_SECRET_KEY>`. La prueba `stripe-client.spec.ts` usa `password = "hunter2hunter2"`: en una ruta de prueba la heurística de credencial asignada no avisa, así que no hace falta marca.

**escanear.** La persona añade `.env` a `.gitignore` y saca el archivo del índice. Luego:

```
python3 $P/scripts/secretos.py --informe
secretos: 3 archivos revisados, 0 hallazgos
informe: uxyngraphar/trabajo/secretos-y-credenciales/informes/escaneo-20261106-175525.md
```

`verificar.py` sin errores.

## Resultado

- El cliente lee `STRIPE_SECRET_KEY` del entorno; `.env.example` la documenta sin valor.
- La persona sabe qué clave revisar y la rotación queda en sus manos.
- Ni el valor de la clave ni el contenido de `.env` aparecen en la respuesta, en el informe ni en el commit.
