// Llamadas a la API del panel. Al abrirlo, la URL trae un código de un solo uso (#c=…) que se canjea por una cookie
// HttpOnly: la página nunca ve ni guarda el token, y la URL del historial ya no abre el panel.

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

export async function api(ruta, datos, metodo) {
  const m = metodo || (datos ? "POST" : "GET");
  let url = ruta;
  const opciones = { method: m, headers: { "Content-Type": "application/json" }, credentials: "same-origin" };
  if (m === "POST") opciones.body = JSON.stringify(datos || {});
  else if (datos) url += "?" + new URLSearchParams(datos);
  let respuesta;
  try {
    respuesta = await fetch(url, opciones);
  } catch {
    alPerderConexion();
    throw new ErrorApi("No hay conexión con el panel.");
  }
  let cuerpo = {};
  try { cuerpo = await respuesta.json(); } catch { /* respuesta vacía */ }
  if (respuesta.ok) return cuerpo.ok;
  const e = typeof cuerpo.error === "object" && cuerpo.error ? cuerpo.error : { mensaje: cuerpo.error || "", codigo: "", accion: "" };
  if (respuesta.status === 403 && e.accion === "abrir_de_nuevo") {
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

export function latir(segundos = 20) {
  const latido = () => enviar("/api/latido").catch(() => {});
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
