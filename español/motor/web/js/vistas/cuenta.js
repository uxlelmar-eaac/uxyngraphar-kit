// Cuenta: hub de sesión, conexiones, herramienta y logs (ADR 0015).

import { h, cabecera, boton, icono } from "../ui.js";
import { panelLogs } from "./logs-ui.js";
import { tarjetaCreador } from "./creador.js";

function tarjetaCuenta(titulo, iconoNombre, texto, accion) {
  return h("div", { class: "tarjeta tarjeta-item" },
    h("h3", {}, icono(iconoNombre), ` ${titulo}`),
    h("p", { class: "tenue", texto }),
    boton("Abrir", accion, { clase: "primario pequeno" }));
}

export async function vista(params, { ir }) {
  const pestana = params.pestana || "inicio";

  if (pestana === "logs") {
    const logs = panelLogs({ colapsable: false, titulo: "Logs del panel" });
    return h("div", {},
      cabecera("Logs", "Registro del panel (API, uxyn, sync). No compite con el taller.",
        boton("Volver a Cuenta", () => ir("cuenta"), { clase: "pequeno fantasma" })),
      logs.nodo);
  }

  if (pestana === "borradores") {
    return h("div", {},
      cabecera("Borradores en la web", "Puente web ↔ este equipo.",
        boton("Volver a Cuenta", () => ir("cuenta"), { clase: "pequeno fantasma" })),
      await tarjetaCreador({ alTraer: async (r, slug) => ir("creador", { id: r?.id || slug }) }));
  }

  return h("div", {},
    cabecera("Cuenta", "Sesión, conexiones, sincronización y registro. Los logs viven aquí, no en el taller."),
    h("div", { class: "rejilla" },
      tarjetaCuenta("Herramienta y sesión", "herramienta", "Versión, actualizar, reparar y cerrar sesión.", () => ir("herramienta")),
      tarjetaCuenta("Conexiones", "conexiones", "Cuenta web, IA local y suscripciones.", () => ir("conexiones")),
      tarjetaCuenta("Borradores web", "subir", "Traer o subir borradores. También desde la barra de salida del Taller.", () => ir("cuenta", { pestana: "borradores" })),
      tarjetaCuenta("Logs", "lista", "Eventos del panel, turnos de uxyn y errores.", () => ir("cuenta", { pestana: "logs" }))));
}
