// Flujo del asistente: diagrama para verlo, una frase que lo explica y un editor para cambiarlo sin escribir ids ni JSON.

import { h, vaciar } from "./ui.js";

// Iconos propios del flujo (mismo trazo que los de ui.js).
const TRAZOS = {
  pedido: "M4 5h16v11H9l-5 4z",
  mano: "M8 11V5a1.5 1.5 0 0 1 3 0v5M11 10V4a1.5 1.5 0 0 1 3 0v6M14 10V5.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-1a6 6 0 0 1-5-2.7L3 14.5a1.5 1.5 0 0 1 2.4-1.8L8 15",
  ojo: "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
  ancla: "M12 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM12 8v13M5 13a7 7 0 0 0 14 0M8 12H5M19 12h-3",
  pasos: "M4 6h3v3H4zM4 15h3v3H4zM10 7.5h10M10 16.5h10M5.5 9v6",
  resultado: "M5 12l5 5 9-10",
  sistema: "M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5",
  flecha: "M5 12h14M13 6l6 6-6 6",
  mas: "M12 5v14M5 12h14",
  quitar: "M6 6l12 12M18 6L6 18",
};

export function iconoFlujo(nombre, clase = "") {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  for (const [k, v] of Object.entries({ viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", "stroke-width": "2",
    "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true" })) svg.setAttribute(k, v);
  if (clase) svg.setAttribute("class", clase);
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
  p.setAttribute("d", TRAZOS[nombre] || "");
  svg.append(p);
  return svg;
}

// `titulo` y `texto` los usan también otras vistas (Mis proyectos); `icono`, `tono` y `ejemplo` son de esta pieza.
export const MODOS = {
  manual: { titulo: "Solo cuando lo pida", texto: "El asistente usa un sistema únicamente si lo nombras en tu pedido.",
    icono: "mano", tono: "neutro", ejemplo: "Ideal para empezar: tú decides en cada pedido." },
  leer_por_defecto: { titulo: "Tenerlos presentes", texto: "Lee estos sistemas en cada pedido, pero solo aplica los que nombres.",
    icono: "ojo", tono: "bien", ejemplo: "Para que conozca tus normas sin aplicarlas siempre." },
  trabajar_con: { titulo: "Sistema base", texto: "Aplica siempre un sistema base en cada pedido, además de los que nombres.",
    icono: "ancla", tono: "acento", ejemplo: "Para una regla que debe cumplirse siempre." },
  secuencia: { titulo: "Pasos en orden", texto: "Recorre estos sistemas uno tras otro, en el orden que elijas.",
    icono: "pasos", tono: "aviso", ejemplo: "Para un proceso fijo: primero esto, luego aquello." },
};

export const FLUJO_VACIO = { formato: 1, modo: "manual", leer_por_defecto: [], trabajar_con: null, secuencia: [], conflictos: "preguntar" };

const titulo = (sistemas, id) => (sistemas.find((p) => p.id === id) || {}).titulo || id;
const enumerar = (xs) => xs.length <= 1 ? (xs[0] || "") : `${xs.slice(0, -1).join(", ")} y ${xs[xs.length - 1]}`;

// Una frase en lenguaje llano con lo que hará el asistente.
export function resumen(flujo, sistemas) {
  const f = { ...FLUJO_VACIO, ...(flujo || {}) };
  const nombres = (ids) => ids.map((id) => `«${titulo(sistemas, id)}»`);
  if (f.modo === "leer_por_defecto") return f.leer_por_defecto.length
    ? `En cada pedido tendrá presentes ${enumerar(nombres(f.leer_por_defecto))}, pero solo aplicará los que nombres.`
    : "Aún no has elegido qué sistemas debe tener presentes.";
  if (f.modo === "trabajar_con") return f.trabajar_con
    ? `En cada pedido aplicará siempre ${nombres([f.trabajar_con])[0]}, además de los que nombres.`
    : "Aún no has elegido el sistema base.";
  if (f.modo === "secuencia") return f.secuencia.length
    ? `Seguirá ${f.secuencia.length === 1 ? "un paso" : `${f.secuencia.length} pasos en orden`}: ${nombres(f.secuencia).join(" → ")}.`
    : "Aún no has añadido pasos.";
  return "Solo usará un sistema cuando lo nombres en tu pedido.";
}

const nodo = (texto, { clase = "", detalle = "", icono = "", numero = null } = {}) => h("div", { class: `nodo ${clase}`.trim() },
  numero !== null ? h("span", { class: "nodo-numero", texto: String(numero) }) : icono ? iconoFlujo(icono, "nodo-icono") : null,
  h("span", { class: "nodo-texto" }, texto, detalle ? h("small", { texto: detalle }) : null));
const flecha = () => h("span", { class: "flecha" }, iconoFlujo("flecha"));

export function diagrama(flujo, sistemas, { compacto = false } = {}) {
  const f = { ...FLUJO_VACIO, ...(flujo || {}) };
  const partes = [nodo("Tu pedido", { clase: "extremo", icono: "pedido" })];
  if (f.modo === "manual") partes.push(flecha(), nodo("Sistemas que nombres", { detalle: "solo si los pides", icono: "mano" }));
  if (f.modo === "leer_por_defecto") partes.push(flecha(), nodo(`Tiene presentes ${f.leer_por_defecto.length}`,
    { icono: "ojo", detalle: f.leer_por_defecto.map((id) => titulo(sistemas, id)).join(", ") || "ninguno aún" }), flecha(), nodo("Aplica los que nombres", { icono: "mano" }));
  if (f.modo === "trabajar_con") partes.push(flecha(), nodo(f.trabajar_con ? titulo(sistemas, f.trabajar_con) : "Sin elegir",
    { clase: "base", icono: "ancla", detalle: "sistema base, siempre" }), flecha(), nodo("+ los que nombres", { icono: "mano" }));
  if (f.modo === "secuencia") {
    if (!f.secuencia.length) partes.push(flecha(), nodo("Sin pasos aún", { icono: "pasos" }));
    f.secuencia.forEach((id, i) => partes.push(flecha(), nodo(titulo(sistemas, id), { clase: i === 0 ? "base" : "", numero: i + 1 })));
  }
  partes.push(flecha(), nodo("Resultado", { clase: "extremo final", icono: "resultado" }));
  return h("div", { class: `diagrama tono-${MODOS[f.modo]?.tono || "neutro"}${compacto ? " compacto" : ""}`, role: "img",
    "aria-label": `Flujo: ${MODOS[f.modo]?.titulo || f.modo}. ${resumen(f, sistemas)}` }, partes);
}

// Ficha de un sistema que se marca o desmarca con un clic.
function ficha(p, marcado, alPulsar, { tipo = "checkbox" } = {}) {
  return h("button", { type: "button", class: "ficha-sistema", role: tipo, "aria-checked": String(marcado), onclick: alPulsar },
    h("span", { class: "ficha-marca", "aria-hidden": "true" }, marcado ? iconoFlujo("resultado") : null),
    h("span", { class: "ficha-texto" }, h("b", { texto: p.titulo }), p.descripcion ? h("small", { texto: p.descripcion }) : null));
}

// Editor. `sistemas`: [{id, titulo, descripcion}] que el flujo puede usar. Devuelve { nodo, valor() }.
export function editorFlujo(flujoInicial, sistemas, alCambiar = () => {}) {
  const f = { ...FLUJO_VACIO, ...(flujoInicial || {}) };
  f.leer_por_defecto = [...f.leer_por_defecto];
  f.secuencia = [...f.secuencia];
  const raiz = h("div", { class: "pila editor-flujo" });
  const nombreGrupo = "modo-" + Math.random().toString(36).slice(2);

  function valor() {
    return { formato: 1, conflictos: "preguntar", modo: f.modo,
      leer_por_defecto: f.modo === "leer_por_defecto" ? f.leer_por_defecto : [],
      trabajar_con: f.modo === "trabajar_con" ? f.trabajar_con : null,
      secuencia: f.modo === "secuencia" ? f.secuencia : [] };
  }

  function cambiar() { pintar(); alCambiar(valor()); }

  function selectorModo() {
    return h("div", { class: "modos", role: "radiogroup", "aria-label": "Cómo trabaja el asistente" },
      Object.entries(MODOS).map(([id, m]) => h("label", { class: `modo tono-${m.tono}` },
        h("input", { type: "radio", name: nombreGrupo, value: id, checked: f.modo === id, onchange: () => { f.modo = id; cambiar(); } }),
        h("span", { class: "modo-icono" }, iconoFlujo(m.icono)),
        h("b", { texto: m.titulo }), h("div", { class: "tenue", texto: m.texto }),
        m.ejemplo ? h("div", { class: "modo-ejemplo", texto: m.ejemplo }) : null)));
  }

  function detalle() {
    if (!sistemas.length && f.modo !== "manual") return h("p", { class: "banda aviso", texto: "Primero elige o instala algún sistema." });
    if (f.modo === "leer_por_defecto") {
      return h("div", { class: "pila" }, h("h3", { texto: "¿Qué sistemas debe tener presentes?" }),
        h("div", { class: "fichas" }, sistemas.map((p) => ficha(p, f.leer_por_defecto.includes(p.id), () => {
          f.leer_por_defecto = f.leer_por_defecto.includes(p.id) ? f.leer_por_defecto.filter((x) => x !== p.id) : [...f.leer_por_defecto, p.id];
          cambiar();
        }))));
    }
    if (f.modo === "trabajar_con") {
      return h("div", { class: "pila" }, h("h3", { texto: "Elige el sistema base (se aplica en cada pedido)" }),
        h("div", { class: "fichas", role: "radiogroup", "aria-label": "Sistema base" }, sistemas.map((p) => ficha(p, f.trabajar_con === p.id, () => {
          f.trabajar_con = f.trabajar_con === p.id ? null : p.id;
          cambiar();
        }, { tipo: "radio" }))));
    }
    if (f.modo === "secuencia") return editorPasos();
    return h("p", { class: "tenue", texto: "No hace falta nada más: cuando quieras usar un sistema, nómbralo en tu pedido." });
  }

  function editorPasos() {
    const lista = h("ol", { class: "pasos" });
    let arrastrado = null;
    f.secuencia.forEach((id, i) => {
      const mover = (d) => { const j = i + d; [f.secuencia[i], f.secuencia[j]] = [f.secuencia[j], f.secuencia[i]]; cambiar(); };
      const li = h("li", { draggable: true },
        h("span", { class: "asa", title: "Arrastra para reordenar", "aria-hidden": "true", texto: "⠿" }),
        h("span", { class: "numero", texto: String(i + 1) }), h("span", { class: "espacio", texto: titulo(sistemas, id) }),
        h("button", { type: "button", class: "boton pequeno fantasma", disabled: i === 0, "aria-label": "Subir paso", title: "Subir", onclick: () => mover(-1) }, "↑"),
        h("button", { type: "button", class: "boton pequeno fantasma", disabled: i === f.secuencia.length - 1, "aria-label": "Bajar paso", title: "Bajar", onclick: () => mover(1) }, "↓"),
        h("button", { type: "button", class: "boton pequeno fantasma", "aria-label": "Quitar paso", title: "Quitar", onclick: () => { f.secuencia.splice(i, 1); cambiar(); } }, iconoFlujo("quitar")));
      li.addEventListener("dragstart", () => { arrastrado = i; li.classList.add("arrastrando"); });
      li.addEventListener("dragend", () => li.classList.remove("arrastrando"));
      li.addEventListener("dragover", (e) => e.preventDefault());
      li.addEventListener("drop", (e) => {
        e.preventDefault();
        if (arrastrado === null || arrastrado === i) return;
        const [movido] = f.secuencia.splice(arrastrado, 1);
        f.secuencia.splice(i, 0, movido);
        cambiar();
      });
      lista.append(li);
    });
    const libres = sistemas.filter((p) => !f.secuencia.includes(p.id));
    return h("div", { class: "pila" }, h("h3", { texto: "Pasos (arrastra o usa las flechas para ordenarlos)" }),
      f.secuencia.length ? lista : h("p", { class: "tenue", texto: "Aún no hay pasos. Pulsa un sistema de abajo para añadirlo como paso." }),
      libres.length ? h("div", { class: "pila" }, h("div", { class: "tenue", texto: "Añadir como siguiente paso:" }),
        h("div", { class: "fila" }, libres.map((p) => h("button", { type: "button", class: "chip-anadir", onclick: () => { f.secuencia.push(p.id); cambiar(); } },
          iconoFlujo("mas"), p.titulo)))) : null);
  }

  function pintar() {
    vaciar(raiz, h("h3", { texto: "Así trabajará el asistente" }), diagrama(valor(), sistemas),
      h("p", { class: "resumen-flujo", texto: resumen(valor(), sistemas) }),
      h("h3", { texto: "¿Cómo quieres que trabaje?", style: "margin-top:8px" }), selectorModo(), detalle());
  }

  pintar();
  return { nodo: raiz, valor };
}
