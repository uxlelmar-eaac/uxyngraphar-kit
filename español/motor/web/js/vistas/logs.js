// Compat: #/logs redirige a Cuenta → Logs (ADR 0015).

import { h } from "../ui.js";

export async function vista(_params, { ir }) {
  ir("cuenta", { pestana: "logs" });
  return h("p", { class: "tenue", texto: "Abriendo logs en Cuenta…" });
}
