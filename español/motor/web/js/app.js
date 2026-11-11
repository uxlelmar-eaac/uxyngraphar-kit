// Arranque del panel: navegación por #/sección, latido para que el servidor sepa que hay una pestaña abierta y cierre.

import { canjearCodigo, VIENE_CON_CODIGO, BIENVENIDA_EN_URL, obtener, enviar, latir, cuandoSeDesconecte } from "./api.js";
import { h, vaciar, icono, cargando, avisar, confirmar } from "./ui.js";
import * as inicio from "./vistas/inicio.js";
import * as proyectos from "./vistas/proyectos.js";
import * as proyecto from "./vistas/proyecto.js";
import * as flujos from "./vistas/flujos.js";
import * as catalogo from "./vistas/catalogo.js";
import * as herramienta from "./vistas/herramienta.js";
import * as bienvenida from "./vistas/bienvenida.js";

const VISTAS = { inicio, proyectos, proyecto, flujos, catalogo, herramienta, bienvenida };
const SECCION_DE = { proyecto: "proyectos" };
const main = document.getElementById("contenido");
const avanzado = document.getElementById("modo-avanzado");

export const modoAvanzado = () => avanzado.checked;

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
    const nodo = await VISTAS[vista].vista(params, { ir, recargar: pintar, modoAvanzado });
    if (propio === turno) vaciar(main, nodo);
  } catch (e) {
    if (propio === turno) vaciar(main, h("div", { class: "banda mal" }, e.message || String(e)));
  }
  main.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}

async function arrancar() {
  for (const a of document.querySelectorAll("#navegacion a")) a.prepend(icono(a.dataset.icono));
  avanzado.checked = localStorage.getItem("uxyn-avanzado") === "1";
  avanzado.addEventListener("change", () => { localStorage.setItem("uxyn-avanzado", avanzado.checked ? "1" : "0"); pintar(); });
  document.getElementById("cerrar-panel").addEventListener("click", async () => {
    const r = await confirmar({ titulo: "Cerrar el panel", texto: "Se apagará el panel y se liberará su puerto. Podrás abrirlo de nuevo con el acceso directo o el comando uxyngraphar.", si: "Cerrar" });
    if (r) { await enviar("/api/cerrar").catch(() => {}); mostrarDesconectado(); }
  });
  cuandoSeDesconecte(mostrarDesconectado);
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
  document.getElementById("version-lateral").textContent = "versión " + sesion.version;
  latir(Math.max(5, Math.min(20, Math.floor((sesion.inactividad || 60) / 4))));
  window.addEventListener("hashchange", pintar);
  if (VIENE_CON_CODIGO) history.replaceState(null, "", location.pathname + ((sesion.bienvenida || BIENVENIDA_EN_URL) ? "#/bienvenida" : "#/inicio"));
  pintar();
}

function mostrarDesconectado() {
  document.getElementById("desconectado").hidden = false;
}

window.addEventListener("unhandledrejection", (e) => avisar(e.reason?.message || "Algo salió mal.", "mal"));
arrancar();
