// Piezas del chat de uxyn (agente del Creador), las mismas que en la web (inspiradas en Deo, el agente de uxconstructar):
// texto con formato seguro, pasos con etiquetas humanas, «trabajando…» con el progreso en vivo y pie con hora y copiar.

import { obtener } from "../api.js";
import { h, vaciar, icono } from "../ui.js";

/** Cada cuánto se pregunta por el progreso mientras el agente trabaja (igual que la web). */
export const SONDEO_MS = 900;

/** Identificador para seguir el progreso de un turno. */
export function nuevoIdProgreso() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `t-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

/** Negritas (**x**) y código (`x`) de una línea como nodos (nunca HTML del modelo). */
function enLinea(linea) {
  const salida = [];
  const patron = /\*\*([^*]+)\*\*|`([^`]+)`/g;
  let ultimo = 0;
  let m;
  while ((m = patron.exec(linea))) {
    if (m.index > ultimo) salida.push(linea.slice(ultimo, m.index));
    salida.push(m[1] !== undefined ? h("strong", { texto: m[1] }) : h("code", { texto: m[2] }));
    ultimo = m.index + m[0].length;
  }
  if (ultimo < linea.length) salida.push(linea.slice(ultimo));
  return salida;
}

const VINETA = /^\s*[-*•]\s+/;
const NUMERO = /^\s*\d+[.)]\s+/;

/** Texto del agente con un subconjunto seguro de Markdown: párrafos, listas, **negritas** y `código`. */
export function textoAgente(texto) {
  const bloques = [];
  const lineas = String(texto || "").replace(/\r\n/g, "\n").split("\n");
  let i = 0;
  while (i < lineas.length) {
    if (!lineas[i].trim()) { i++; continue; }
    const tipo = VINETA.test(lineas[i]) ? "ul" : NUMERO.test(lineas[i]) ? "ol" : null;
    if (tipo) {
      const marca = tipo === "ul" ? VINETA : NUMERO;
      const items = [];
      while (i < lineas.length && marca.test(lineas[i])) items.push(h("li", {}, enLinea(lineas[i++].replace(marca, ""))));
      bloques.push(h(tipo, {}, items));
      continue;
    }
    const parrafo = [];
    while (i < lineas.length && lineas[i].trim() && !VINETA.test(lineas[i]) && !NUMERO.test(lineas[i])) parrafo.push(lineas[i++]);
    bloques.push(h("p", {}, parrafo.map((l, j) => [j ? h("br", {}) : null, enLinea(l)])));
  }
  return h("div", { class: "texto-agente" }, bloques);
}

const ESTADOS = { running: "en curso", ok: "hecho", failed: "falló" };

/** Pasos del agente: [{etiqueta, estado: running|ok|failed}]. */
export function pasosAgente(pasos) {
  if (!pasos?.length) return null;
  return h("ul", { class: "pasos-agente", "aria-label": "Pasos del agente" },
    pasos.map((p) => h("li", { class: `paso-${p.estado}` },
      p.estado === "running" ? h("span", { class: "giro chico", "aria-hidden": "true" }) : icono(p.estado === "ok" ? "check" : "cerrar"),
      h("span", { texto: p.etiqueta || p.herramienta }),
      h("span", { class: "solo-lector", texto: ESTADOS[p.estado] || "" }))));
}

/** Las acciones guardadas de una respuesta como pasos terminados. */
export const pasosDeAcciones = (acciones) =>
  (acciones || []).map((a) => ({ herramienta: a.herramienta, etiqueta: a.etiqueta || a.resumen, estado: a.ok ? "ok" : "failed" }));

/** Hora y botón de copiar bajo una respuesta del agente. */
export function pieMensaje(texto, fecha = new Date()) {
  const copiar = h("button", { type: "button", class: "copiar-mensaje", title: "Copiar respuesta", "aria-label": "Copiar respuesta" }, icono("copiar"));
  copiar.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(texto);
      copiar.setAttribute("aria-label", "Copiado");
      copiar.title = "Copiado";
      vaciar(copiar, icono("check"));
      setTimeout(() => { copiar.setAttribute("aria-label", "Copiar respuesta"); copiar.title = "Copiar respuesta"; vaciar(copiar, icono("copiar")); }, 1800);
    } catch { /* sin portapapeles */ }
  });
  const hora = fecha instanceof Date && !Number.isNaN(fecha.getTime())
    ? h("time", { datetime: fecha.toISOString(), texto: fecha.toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit" }) }) : null;
  return h("div", { class: "pie-mensaje" }, hora, texto ? copiar : null);
}

/** Respuesta del agente: avatar, texto con formato, pasos hechos, extras (botones) y pie. */
export function mensajeAgente(texto, { acciones = [], extra = [], fecha, error = false, quien = "uxyn" } = {}) {
  return h("div", { class: "mensaje-agente" },
    h("span", { class: "avatar-agente", "aria-hidden": "true" }, icono("creador")),
    h("div", { class: `mensaje ia${error ? " error" : ""}` },
      h("span", { class: "quien", texto: quien }),
      error ? h("p", { role: "alert", texto }) : textoAgente(texto),
      pasosAgente(pasosDeAcciones(acciones)),
      extra,
      error ? null : pieMensaje(texto, fecha ? new Date(fecha) : new Date())));
}

/**
 * «El asistente está trabajando…» con los pasos en vivo: consulta el progreso del turno mientras espera la respuesta.
 * `seguir(id)` empieza a consultar; `parar()` deja de hacerlo y quita el nodo.
 */
export function trabajando({ pista = "" } = {}) {
  const etiqueta = h("b", { texto: "Pensando" });
  const pasos = h("div", {});
  const nodo = h("div", { class: "mensaje-agente trabajando", role: "status", "aria-live": "polite", "aria-busy": "true" },
    h("span", { class: "avatar-agente", "aria-hidden": "true" }, icono("creador")),
    h("div", { class: "mensaje ia" },
      h("p", { class: "fila" }, etiqueta, h("span", { class: "puntos", "aria-hidden": "true" }, h("span", {}), h("span", {}), h("span", {}))),
      pista ? h("p", { class: "tenue", texto: pista }) : null,
      pasos));
  let temporizador = null;
  let actual = null;
  function pintar(p) {
    etiqueta.textContent = p?.fase === "cerrando" ? "Resumiendo lo que hizo" : p?.pasos?.length ? "Trabajando en tu sistema" : "Pensando";
    vaciar(pasos, pasosAgente(p?.pasos || []));
  }
  return {
    nodo,
    seguir(id) {
      actual = id;
      pintar(null);
      clearInterval(temporizador);
      temporizador = setInterval(async () => {
        try {
          const p = await obtener("/api/agente/progreso", { id });
          if (actual === id) pintar(p);
        } catch { /* sin progreso: solo no se ven los pasos */ }
      }, SONDEO_MS);
    },
    parar() {
      actual = null;
      clearInterval(temporizador);
      nodo.remove();
    },
  };
}
