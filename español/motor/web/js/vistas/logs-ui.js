// Piezas compartidas del visor de Logs (cajón del Creador y sección global).

import { h, vaciar, boton, avisar } from "../ui.js";
import {
  listar, vaciar as vaciarRegistro, suscribir, exportarTexto, contadorErrores,
  incorporarServidor,
} from "../registro.js";
import { obtener } from "../api.js";

function hora(iso) {
  try {
    return new Date(iso).toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return iso || "";
  }
}

function fila(e) {
  return h("article", { class: `log-fila log-${e.nivel}`, "data-origen": e.origen },
    h("div", { class: "log-meta" },
      h("span", { class: "log-hora", texto: hora(e.t) }),
      h("span", { class: "log-origen", texto: e.origen }),
      e.ms != null ? h("span", { class: "tenue", texto: `${e.ms} ms` }) : null,
      e.ok === false ? h("span", { class: "log-bad", texto: "falló" }) : null),
    h("p", { class: "log-titulo", texto: e.titulo }),
    e.detalle ? h("p", { class: "tenue log-detalle", texto: e.detalle }) : null,
    e.datos !== undefined
      ? h("details", { class: "log-datos" },
          h("summary", { texto: "Datos" }),
          h("pre", { texto: (() => { try { return JSON.stringify(e.datos, null, 2); } catch { return String(e.datos); } })() }))
      : null);
}

/**
 * Panel de logs reutilizable.
 * Devuelve { nodo, refrescar, abrir, cerrar, destruir }.
 * `colapsable`: si true, empieza cerrado (cajón).
 */
export function panelLogs({ colapsable = false, titulo = "Logs", conOrigen = false } = {}) {
  let nivel = "";
  let origen = "";
  let abierto = !colapsable;
  const lista = h("div", { class: "log-lista", role: "log", "aria-live": "polite" });
  const badge = h("span", { class: "insignia nota log-badge", hidden: true, texto: "0" });
  const cuerpo = h("div", { class: "log-cuerpo" }, lista);
  const selNivel = h("select", { "aria-label": "Filtrar por nivel", class: "breve" },
    h("option", { value: "", texto: "Todos los niveles" }),
    h("option", { value: "error", texto: "Solo errores" }),
    h("option", { value: "aviso", texto: "Avisos" }),
    h("option", { value: "info", texto: "Info" }));
  const selOrigen = conOrigen
    ? h("select", { "aria-label": "Filtrar por origen", class: "breve" },
        h("option", { value: "", texto: "Todos los orígenes" }),
        ["api", "agente", "creador", "panel", "sistema"].map((o) => h("option", { value: o, texto: o })))
    : null;

  function pintarLista() {
    const items = listar({ nivel: nivel || undefined, origen: origen || undefined });
    vaciar(lista, items.length
      ? items.map(fila)
      : h("p", { class: "tenue", texto: "Aún no hay eventos. Las llamadas del panel y los turnos de uxyn aparecen aquí." }));
    const n = contadorErrores();
    badge.textContent = String(n);
    badge.hidden = n === 0;
  }

  async function traerServidor() {
    try {
      const r = await obtener("/api/registros", {});
      incorporarServidor(Array.isArray(r) ? r : []);
    } catch { /* sin endpoint o sin sesión */ }
  }

  selNivel.addEventListener("change", () => { nivel = selNivel.value; pintarLista(); });
  if (selOrigen) selOrigen.addEventListener("change", () => { origen = selOrigen.value; pintarLista(); });

  const barra = h("div", { class: "fila log-barra" },
    selNivel,
    selOrigen,
    h("span", { class: "espacio" }),
    boton("Copiar", async () => {
      try {
        await navigator.clipboard.writeText(exportarTexto({
          nivel: nivel || undefined,
          origen: origen || undefined,
        }));
        avisar("Logs copiados");
      } catch {
        avisar("No se pudo copiar", "mal");
      }
    }, { clase: "pequeno" }),
    boton("Vaciar", () => { vaciarRegistro(); pintarLista(); }, { clase: "pequeno" }),
    boton("Actualizar", async () => { await traerServidor(); pintarLista(); }, { clase: "pequeno" }));

  const cab = colapsable
    ? h("button", { type: "button", class: "log-toggle", "aria-expanded": "false" },
        h("span", { texto: titulo }), badge, h("span", { class: "tenue", texto: "mostrar u ocultar" }))
    : h("div", { class: "fila separada" }, h("h2", { texto: titulo }), badge);

  if (colapsable) {
    cuerpo.hidden = true;
    barra.hidden = true;
    cab.addEventListener("click", () => {
      abierto = !abierto;
      cuerpo.hidden = !abierto;
      barra.hidden = !abierto;
      cab.setAttribute("aria-expanded", String(abierto));
      if (abierto) void traerServidor().then(pintarLista);
    });
  }

  const nodo = h("section", { class: "logs-panel" + (colapsable ? " logs-cajon" : ""), "aria-label": titulo },
    cab, colapsable ? null : barra, cuerpo, colapsable ? barra : null);

  const quitar = suscribir(() => {
    pintarLista();
    if (colapsable && !abierto && contadorErrores() > 0) {
      abierto = true;
      cuerpo.hidden = false;
      barra.hidden = false;
      cab.setAttribute("aria-expanded", "true");
    }
  });
  pintarLista();
  void traerServidor().then(pintarLista);

  return {
    nodo,
    refrescar: async () => { await traerServidor(); pintarLista(); },
    abrir: () => {
      if (!colapsable) return;
      abierto = true;
      cuerpo.hidden = false;
      barra.hidden = false;
      cab.setAttribute("aria-expanded", "true");
      void traerServidor().then(pintarLista);
    },
    destruir: () => quitar(),
  };
}
