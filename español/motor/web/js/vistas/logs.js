// Sección global «Logs» del panel.

import { h, cabecera } from "../ui.js";
import { panelLogs } from "./logs-ui.js";
import { anotar } from "../registro.js";

export async function vista() {
  anotar({ nivel: "info", origen: "sistema", titulo: "Vista Logs abierta" });
  const panel = panelLogs({ colapsable: false, titulo: "Actividad del panel", conOrigen: true });
  return h("div", {},
    cabecera("Logs", "Todo lo que hace el panel en esta sesión: API, uxyn, traer borradores y errores."),
    panel.nodo);
}
