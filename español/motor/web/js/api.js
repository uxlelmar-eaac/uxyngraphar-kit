// Llamadas a la API del panel. Al abrirlo, la URL trae un código de un solo uso (#c=…) que se canjea por una cookie
// HttpOnly: la página nunca ve ni guarda el token, y la URL del historial ya no abre el panel.

import { anotar, debeOmitirRuta, resumir } from "./registro.js";

const CODIGO = new URLSearchParams(location.hash.replace(/^#\/?/, "").split("?")[0]).get("c") || "";
export const BIENVENIDA_EN_URL = /[#&]bienvenida=1/.test(location.hash);
export const VIENE_CON_CODIGO = Boolean(CODIGO);

// Canjea el código de la URL (si lo hay) por la cookie de sesión. Sin código, vale la cookie que ya tenga la pestaña.
export async function canjearCodigo() {
  if (!CODIGO) return true;
  try {
    const r = await fetch("/api/canjear", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codigo: CODIGO }), credentials: "same-origin" });
    return r.ok;
  } catch {
    return false;
  }
}

// Errores de la API (M-25): {"error": {codigo, mensaje, accion}}. `accion` sugiere qué puede hacer la persona.
export class ErrorApi extends Error {
  constructor(mensaje, codigo = "", accion = "") { super(mensaje); this.codigo = codigo; this.accion = accion; }
}

let alPerderConexion = () => {};
export function cuandoSeDesconecte(funcion) { alPerderConexion = funcion; }

// La pestaña perdió el permiso (403 «abrir_de_nuevo»): el panel se reinició con otra sesión, p. ej. tras actualizar.
let alPerderSesion = () => {};
export function cuandoPierdaSesion(funcion) { alPerderSesion = funcion; }

export async function api(ruta, datos, metodo) {
  const m = metodo || (datos ? "POST" : "GET");
  let url = ruta;
  const opciones = { method: m, headers: { "Content-Type": "application/json" }, credentials: "same-origin" };
  if (m === "POST") opciones.body = JSON.stringify(datos || {});
  else if (datos) url += "?" + new URLSearchParams(datos);
  const t0 = performance.now();
  const silencioso = debeOmitirRuta(ruta);
  let respuesta;
  try {
    respuesta = await fetch(url, opciones);
  } catch {
    // Latido y otras rutas silenciosas no deben tapar la UI con «El panel se cerró»
    // por un fallo de red puntual.
    if (!silencioso) alPerderConexion();
    if (!silencioso) {
      anotar({
        nivel: "error", origen: "api", titulo: `${m} ${ruta} (sin conexión)`,
        ruta, ms: Math.round(performance.now() - t0), ok: false,
      });
    }
    throw new ErrorApi("No hay conexión con el panel.");
  }
  let cuerpo = {};
  try { cuerpo = await respuesta.json(); } catch { /* respuesta vacía */ }
  const ms = Math.round(performance.now() - t0);
  if (respuesta.ok) {
    if (!silencioso) {
      anotar({
        nivel: "info", origen: "api", titulo: `${m} ${ruta}`,
        ruta, ms, ok: true,
        datos: m === "POST" ? { pedido: resumir(datos), respuesta: resumir(cuerpo.ok) } : { respuesta: resumir(cuerpo.ok) },
      });
    }
    return cuerpo.ok;
  }
  const e = typeof cuerpo.error === "object" && cuerpo.error ? cuerpo.error : { mensaje: cuerpo.error || "", codigo: "", accion: "" };
  if (!silencioso) {
    anotar({
      nivel: "error", origen: "api", titulo: `${m} ${ruta} → ${respuesta.status}`,
      ruta, ms, ok: false,
      detalle: e.mensaje || cuerpo.detalle || "",
      datos: { codigo: e.codigo, accion: e.accion, detalle: cuerpo.detalle, registro: cuerpo.registro },
    });
  }
  if (respuesta.status === 403 && e.accion === "abrir_de_nuevo") {
    alPerderSesion();
    throw new ErrorApi("Esta pestaña no tiene permiso. Abre el panel de nuevo con el comando uxyngraphar o su acceso directo.", e.codigo, e.accion);
  }
  if (respuesta.status === 500) {
    throw new ErrorApi(`Error interno del panel (${cuerpo.detalle || "sin detalle"}). Registro: ${cuerpo.registro || "panel.log"}`, e.codigo, e.accion);
  }
  if (e.accion === "registrar" && m === "POST" && datos?.repo && !datos._reintento) {
    const { confirmar } = await import("./ui.js");
    const si = await confirmar({ titulo: "Proyecto fuera de tu lista", texto: `${e.mensaje}\n\n¿Lo añado a «Mis proyectos» y sigo?`, si: "Añadir y seguir" });
    if (si) {
      await api("/api/proyectos/agregar", { rutas: [datos.repo] }, "POST");
      return api(ruta, { ...datos, _reintento: true }, metodo);
    }
  }
  throw new ErrorApi(e.mensaje || "Algo salió mal.", e.codigo, e.accion);
}

export const obtener = (ruta, datos) => api(ruta, datos, "GET");
export const enviar = (ruta, datos) => api(ruta, datos || {}, "POST");

// Clasifica la respuesta de un latido: "ok" (con el estado del servidor), "sin_sesion" (403: otra sesión) o "caido".
export async function latidoUnaVez() {
  try {
    const r = await fetch("/api/latido", { method: "POST", headers: { "Content-Type": "application/json" },
      body: "{}", credentials: "same-origin" });
    if (r.ok) {
      let cuerpo = {};
      try { cuerpo = await r.json(); } catch { /* sin cuerpo */ }
      return { tipo: "ok", estado: (cuerpo && typeof cuerpo.ok === "object" && cuerpo.ok) || {} };
    }
    return { tipo: r.status === 403 ? "sin_sesion" : "caido" };
  } catch {
    return { tipo: "caido" };
  }
}

// Decide qué hacer con un latido. Puro (sin DOM) para poder probarlo:
//  · "recargar": volvió el panel tras una caída o un permiso perdido (la cookie nueva de otra pestaña vale aquí
//    también) o el proceso cambió de versión → se recarga la página con el código nuevo.
//  · "sin_sesion" / "caido": se muestra el aviso correspondiente y se sigue latiendo para reconectar sola.
//  · "version_nueva": autoactualizar instaló otra versión mientras este panel seguía abierto.
export function decidirLatido(resultado, memoria) {
  if (resultado.tipo === "sin_sesion") { memoria.perdida = true; memoria.fallos = 0; return "sin_sesion"; }
  if (resultado.tipo === "caido") {
    memoria.fallos = (memoria.fallos || 0) + 1;
    if (memoria.fallos >= 2) { memoria.perdida = true; return "caido"; }
    return "esperar";
  }
  memoria.fallos = 0;
  const e = resultado.estado || {};
  if (memoria.perdida) return "recargar";
  if (e.version && memoria.version && e.version !== memoria.version) return "recargar";
  if (e.activa && e.version && e.activa !== e.version && memoria.avisadaActiva !== e.activa) {
    memoria.avisadaActiva = e.activa;
    return "version_nueva";
  }
  return "nada";
}

// Latido: el servidor sabe que hay una pestaña abierta y la pestaña nota reinicios, permisos perdidos y versiones nuevas.
export function latir(segundos = 20, versionCargada = "", acciones = {}) {
  const memoria = { version: versionCargada, fallos: 0, perdida: false, avisadaActiva: "" };
  let ocupado = false;
  const latido = async () => {
    if (ocupado) return;
    ocupado = true;
    try {
      const decision = decidirLatido(await latidoUnaVez(), memoria);
      if (decision === "sin_sesion") alPerderSesion();
      else if (decision === "caido") alPerderConexion();
      else if (decision === "recargar") location.reload();
      else if (decision === "version_nueva") acciones.versionNueva?.(memoria.avisadaActiva, memoria.version);
    } finally {
      ocupado = false;
    }
  };
  latido();
  setInterval(latido, segundos * 1000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) latido(); });
}

export async function esperarServidor(intentos = 60) {
  for (let i = 0; i < intentos; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    try {
      const r = await fetch("/api/sesion", { credentials: "same-origin" });
      if (r.ok) return true;
    } catch { /* aún reiniciando */ }
  }
  return false;
}

let catalogoCache = null;
export async function catalogo(recargar = false) {
  if (!catalogoCache || recargar) catalogoCache = await obtener("/api/catalogo");
  return catalogoCache;
}

export const nombreDe = (ruta) => String(ruta || "").split(/[\\/]/).filter(Boolean).pop() || ruta;
