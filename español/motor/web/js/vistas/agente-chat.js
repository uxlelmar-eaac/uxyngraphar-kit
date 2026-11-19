// Piezas del chat de uxyn (agente del Creador), las mismas que en la web (inspiradas en Deo, el agente de uxconstructar):
// texto con formato seguro, pasos con etiquetas humanas, «trabajando…» con el progreso en vivo y pie con hora y copiar.

import { obtener } from "../api.js";
import { h, vaciar, icono, boton } from "../ui.js";
import { anotar } from "../registro.js";

/** El servidor (o el kit) dice que no hay ninguna IA con la que trabajar: sin clave en la cuenta ni plataforma. */
export const RE_SIN_IA = /a[ñn]ade una clave de ia|sin (ninguna )?clave de ia|no hay ninguna ia/i;

/**
 * Qué hacer cuando falta una IA, con opciones concretas (null si el error es otro). No compra ni guarda nada: solo
 * explica dónde añadir una clave y qué opciones locales admite el kit.
 */
export function ayudaSinIA(mensaje, codigo = "") {
  if (codigo !== "uxyn_sin_ia" && !RE_SIN_IA.test(String(mensaje || ""))) return null;
  const item = (titulo, texto) => h("li", {}, h("b", { texto: titulo }), " ", texto);
  return h("div", { class: "pila banda aviso", role: "note", "data-ayuda": "sin-ia" },
    h("b", { texto: "uxyn necesita una IA para proponer cambios. Elige una de estas opciones:" }),
    h("ul", {},
      item("Clave de IA en tu cuenta (para «uxyn (tu cuenta)»):",
        "en la web de uxyngraphar, Cuenta → IA y conexiones → añade la clave de tu proveedor (OpenAI, Anthropic, Google AI Studio…). Se guarda cifrada en el servidor y nunca llega a este equipo."),
      item("Un modelo en este equipo, sin clave:",
        "Ollama (http://127.0.0.1:11434) o LM Studio con su servidor local activo (http://127.0.0.1:1234) y al menos un modelo descargado."),
      item("Tu suscripción, con su CLI oficial instalada y la sesión iniciada:",
        "Claude Code, Codex, GitHub Copilot CLI o Qwen Code.")),
    h("p", {},
      "Con un modelo local o una suscripción, elígelo en «Qué IA usar» y vuelve a intentarlo (Mejorar, Revisar y el chat lo usan). Detalles y avisos de cada suscripción en ",
      h("a", { href: "#/conexiones", texto: "Conexiones" }), "."));
}

/** «Completar el sistema»: el mismo pedido que la web (uxyngraphar-frontend, creator.fillPrompt). */
export const PEDIDO_COMPLETAR = "Completa el sistema entero: primero el núcleo (SISTEMA.md, LIMITES.md, PERMISOS.md, MEMORIAS.md, README.md y sistema.json) y después el resto del esqueleto (proceso/, skills/, HERRAMIENTAS.md, prompts/, config/, plantillas/, referencia/, ejemplos/, pruebas/ y CHANGELOG.md). Sustituye todos los marcadores {{…}} con gobernanza concreta para agentes de IA, crea las piezas que falten y déjalo como sugerencia en «Por revisar». En sistema.json, permisos.acciones.agente y solo_persona son listas de «scripts/….py [subcomando]» (o []); sin texto libre.";

const TIPOS_CAMBIO = { nuevo: ["mas", "nuevo"], cambiado: ["editar", "cambiado"], borrado: ["basura", "borrado"] };

/**
 * Resumen de los archivos que tocan las propuestas de un turno (contrato uxyn 2: acciones[].cambios).
 * Una ruta que aparece en varias propuestas se suma. Devuelve {archivos: [{ruta, tipo, mas, menos}], mas, menos}.
 */
export function resumenCambios(acciones) {
  const porRuta = new Map();
  for (const a of acciones || []) {
    for (const c of Array.isArray(a?.cambios) ? a.cambios : []) {
      if (!c || typeof c.ruta !== "string") continue;
      const tipo = TIPOS_CAMBIO[c.tipo] ? c.tipo : "cambiado";
      const previo = porRuta.get(c.ruta);
      const mas = Number(c.mas) || 0;
      const menos = Number(c.menos) || 0;
      porRuta.set(c.ruta, previo ? { ...previo, tipo, mas: previo.mas + mas, menos: previo.menos + menos } : { ruta: c.ruta, tipo, mas, menos });
    }
  }
  const archivos = [...porRuta.values()];
  return { archivos, mas: archivos.reduce((s, c) => s + c.mas, 0), menos: archivos.reduce((s, c) => s + c.menos, 0) };
}

/** Tarjeta con los archivos que uxyn propone cambiar (+/−) y el botón para revisarlos; null si no hay cambios. */
export function cambiosAgente(acciones, alRevisar = null) {
  const { archivos, mas, menos } = resumenCambios(acciones);
  if (!archivos.length) return null;
  const titulo = archivos.length === 1 ? "1 archivo por revisar" : `${archivos.length} archivos por revisar`;
  return h("div", { class: "tarjeta-cambios", "data-cambios": String(archivos.length) },
    h("div", { class: "fila separada" },
      h("b", { texto: titulo }),
      h("span", { class: "totales-cambios" }, h("span", { class: "cambio-mas", texto: `+${mas}` }), " ", h("span", { class: "cambio-menos", texto: `−${menos}` }))),
    h("ul", { class: "lista-cambios", "aria-label": "Archivos que cambian" },
      archivos.map((c) => h("li", { class: `cambio-${c.tipo}` },
        h("span", { class: "icono-cambio", "aria-hidden": "true" }, icono(TIPOS_CAMBIO[c.tipo][0])),
        h("code", { texto: c.ruta, title: c.ruta }),
        h("span", { class: "tipo-cambio", texto: TIPOS_CAMBIO[c.tipo][1] }),
        h("span", { class: "cambio-mas", texto: `+${c.mas}` }),
        h("span", { class: "cambio-menos", texto: `−${c.menos}` })))),
    alRevisar ? h("div", { class: "fila" }, boton("Revisar y aceptar", alRevisar, { clase: "pequeno primario", icono: "check" })) : null);
}

/** Qué sabe hacer uxyn (GET info → capacidades), plegado bajo el saludo. */
export function capacidadesAgente(info) {
  const lista = Array.isArray(info?.capacidades) ? info.capacidades.filter((c) => c && c.nombre) : [];
  if (!lista.length) return null;
  return h("details", { class: "capacidades-agente" },
    h("summary", { texto: "Qué puede hacer uxyn" }),
    h("ul", {}, lista.map((c) => h("li", {}, h("code", { texto: c.nombre }), " ", c.descripcion || ""))));
}

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
export function mensajeAgente(texto, { acciones = [], extra = [], fecha, error = false, quien = "uxyn", alRevisar = null } = {}) {
  return h("div", { class: "mensaje-agente" },
    h("span", { class: "avatar-agente", "aria-hidden": "true" }, icono("creador")),
    h("div", { class: `mensaje ia${error ? " error" : ""}` },
      h("span", { class: "quien", texto: quien }),
      error ? h("p", { role: "alert", texto }) : textoAgente(texto),
      pasosAgente(pasosDeAcciones(acciones)),
      error ? null : cambiosAgente(acciones, alRevisar),
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
  let ultimoPaso = "";
  function pintar(p) {
    etiqueta.textContent = p?.fase === "cerrando" ? "Resumiendo lo que hizo" : p?.pasos?.length ? "Trabajando en tu sistema" : "Pensando";
    const lista = p?.pasos || [];
    vaciar(pasos, pasosAgente(lista));
    const marca = lista.map((s) => `${s.etiqueta || s.herramienta}:${s.estado}`).join("|");
    if (marca && marca !== ultimoPaso) {
      ultimoPaso = marca;
      const ultimo = lista[lista.length - 1];
      if (ultimo) {
        anotar({
          nivel: ultimo.estado === "failed" ? "error" : "info",
          origen: "agente",
          titulo: `Paso: ${ultimo.etiqueta || ultimo.herramienta || "acción"}`,
          detalle: ultimo.estado || "",
        });
      }
    }
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
