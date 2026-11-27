// Arranque del panel: navegación por #/sección, latido para que el servidor sepa que hay una pestaña abierta y cierre.
// Áreas: Inicio · Taller · Proyectos · Flujos · Mercado · Cuenta (ADR 0015; Flujos volvió al menú: los sistemas se encadenan solo a través de un flujo).

import { canjearCodigo, VIENE_CON_CODIGO, BIENVENIDA_EN_URL, obtener, enviar, latir, cuandoSeDesconecte, cuandoPierdaSesion, esperarServidor } from "./api.js";
import { h, vaciar, icono, cargando, avisar, confirmar } from "./ui.js";
import * as inicio from "./vistas/inicio.js";
import * as proyectos from "./vistas/proyectos.js";
import * as proyecto from "./vistas/proyecto.js";
import * as flujos from "./vistas/flujos.js";
import * as catalogo from "./vistas/catalogo.js";
import * as herramienta from "./vistas/herramienta.js";
import * as creador from "./vistas/creador-sistemas.js";
import * as misSistemas from "./vistas/mis-sistemas.js";
import * as conexiones from "./vistas/conexiones.js";
import * as logs from "./vistas/logs.js";
import * as cuenta from "./vistas/cuenta.js";
import * as bienvenida from "./vistas/bienvenida.js";
import * as revision from "./vistas/revision.js";

const VISTAS = {
  inicio, proyectos, proyecto, flujos, catalogo, creador, conexiones, herramienta, logs, cuenta, bienvenida,
  "mis-sistemas": misSistemas,
  revision,
  // Alias de producto
  taller: creador,
  mercado: catalogo,
};
const SECCION_DE = {
  proyecto: "proyectos",
  creador: "creador",
  taller: "creador",
  "mis-sistemas": "mis-sistemas",
  revision: "mis-sistemas",
  catalogo: "catalogo",
  mercado: "catalogo",
  herramienta: "cuenta",
  conexiones: "cuenta",
  logs: "cuenta",
  flujos: "flujos",
  cuenta: "cuenta",
};
const main = document.getElementById("contenido");
function rutaActual() {
  const limpio = location.hash.replace(/^#\/?/, "");
  if (!limpio || limpio.startsWith("t=")) return { vista: "inicio", params: {} };
  const [vista, consulta] = limpio.split("?");
  return { vista: VISTAS[vista] ? vista : "inicio", params: Object.fromEntries(new URLSearchParams(consulta || "")) };
}

export function ir(vista, params) {
  const destino = "#/" + vista + (params ? "?" + new URLSearchParams(params) : "");
  if (location.hash === destino) pintar();
  else location.hash = destino;
}

let turno = 0;
async function pintar() {
  const { vista, params } = rutaActual();
  const propio = ++turno;
  for (const a of document.querySelectorAll("#navegacion a")) {
    a.classList.toggle("activo", a.dataset.seccion === (SECCION_DE[vista] || vista));
    if (a.dataset.seccion === (SECCION_DE[vista] || vista)) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  }
  vaciar(main, cargando());
  try {
    const nodo = await VISTAS[vista].vista(params, { ir, recargar: pintar });
    if (propio === turno) vaciar(main, nodo);
  } catch (e) {
    if (propio === turno) vaciar(main, h("div", { class: "banda mal" }, e.message || String(e)));
  }
  main.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}

async function arrancar() {
  for (const a of document.querySelectorAll("#navegacion a")) a.prepend(icono(a.dataset.icono));
  try { localStorage.removeItem("uxyn-avanzado"); } catch { /* sin almacenamiento */ }
  document.getElementById("cerrar-panel").addEventListener("click", async () => {
    const r = await confirmar({ titulo: "Cerrar el panel", texto: "Se apagará el panel y se liberará su puerto. Podrás abrirlo de nuevo con el acceso directo o el comando uxyngraphar.", si: "Cerrar" });
    if (r) { await enviar("/api/cerrar").catch(() => {}); mostrarDesconectado("cerrado"); }
  });
  cuandoSeDesconecte(() => mostrarDesconectado("caido"));
  cuandoPierdaSesion(() => mostrarDesconectado("sin_sesion"));
  if (!(await canjearCodigo())) {
    history.replaceState(null, "", location.pathname);
    vaciar(main, h("div", { class: "banda mal" }, "Este enlace ya se usó o caducó. Abre el panel con el comando uxyngraphar o con su acceso directo."));
    return;
  }
  let sesion;
  try {
    sesion = await obtener("/api/sesion");
  } catch (e) {
    vaciar(main, h("div", { class: "banda mal" }, e.message));
    return;
  }
  document.getElementById("desconectado").hidden = true;
  document.getElementById("version-lateral").textContent = "versión " + sesion.version;
  latir(Math.max(5, Math.min(20, Math.floor((sesion.inactividad || 60) / 4))), sesion.version, { versionNueva: avisarVersionNueva });
  window.addEventListener("hashchange", pintar);
  if (VIENE_CON_CODIGO) history.replaceState(null, "", location.pathname + ((sesion.bienvenida || BIENVENIDA_EN_URL) ? "#/bienvenida" : "#/inicio"));
  pintar();
}

// Avisos de pantalla completa. La pestaña sigue latiendo: si el panel vuelve (o se abre de nuevo y la pestaña nueva
// deja su cookie, que vale para todas las del mismo equipo), se recarga sola.
const AVISOS_DESCONEXION = {
  cerrado: ["El panel se cerró",
    "Para volver a abrirlo, usa el acceso directo de uxyngraphar o escribe «uxyngraphar panel» en una terminal."],
  caido: ["Se perdió la conexión con el panel",
    "El panel se cerró o se está reiniciando (por ejemplo, tras actualizar uxyngraphar).\n\nSi vuelve en el mismo puerto, esta pestaña se reconecta sola. Si no, ábrelo con el acceso directo o «uxyngraphar panel»."],
  sin_sesion: ["El panel se reinició: esta pestaña quedó con un permiso viejo",
    "Pasa tras actualizar uxyngraphar o al volver a abrir el panel. Por seguridad, una pestaña antigua no puede seguir sin un permiso nuevo.\n\nAbre el panel con el acceso directo o «uxyngraphar panel»: en cuanto lo hagas, esta pestaña también se reconecta sola (o ciérrala)."],
};

function mostrarDesconectado(motivo = "cerrado") {
  const [titulo, texto] = AVISOS_DESCONEXION[motivo] || AVISOS_DESCONEXION.cerrado;
  const capa = document.getElementById("desconectado");
  const tarjeta = capa.querySelector(".tarjeta");
  vaciar(tarjeta, h("h2", { texto: titulo }), h("p", { texto }));
  capa.dataset.motivo = motivo;
  capa.hidden = false;
}

let versionNuevaAvisada = false;
function avisarVersionNueva(activa, actual) {
  if (versionNuevaAvisada) return;
  versionNuevaAvisada = true;
  const banda = h("div", { class: "banda", role: "status", id: "aviso-version-nueva" },
    h("span", { texto: `Se instaló la versión ${activa} de uxyngraphar, pero este panel sigue con la ${actual}. ` }),
    h("button", { type: "button", texto: `Reiniciar el panel con la ${activa}`, onclick: async (ev) => {
      ev.currentTarget.disabled = true;
      ev.currentTarget.textContent = "Reiniciando…";
      await enviar("/api/reiniciar").catch(() => {});
      if (await esperarServidor()) location.reload();
      else mostrarDesconectado("caido");
    } }));
  main.before(banda);
}

window.addEventListener("unhandledrejection", (e) => avisar(e.reason?.message || "Algo salió mal.", "mal"));
arrancar();
